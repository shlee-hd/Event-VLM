"""
Event-VLM: End-to-end inference pipeline.
Cascaded three-stage framework for efficient video understanding.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Generator, Union
from pathlib import Path
import time
import logging

import torch
import numpy as np
import cv2
from PIL import Image

from src.config import EventVLMConfig, DetectorConfig, PruningConfig, VLMConfig
from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig
from src.detector import DETRDetector, YOLODetector
from src.detector.detr_wrapper import Detection, DetectionResult, get_detector
from src.pruning import TokenPruner
from src.reporting import ReportingContract, ReportingPolicy
from src.vlm import LLaVAWrapper, HazardPriorityPrompting

logger = logging.getLogger(__name__)


@dataclass
class FrameResult:
    """Result for a single frame."""
    frame_idx: int
    timestamp: float
    is_event: bool
    detections: List[Detection]
    hazard_level: str
    caption: Optional[str] = None
    tokens_used: int = 0
    tokens_total: int = 576
    processing_time: float = 0.0
    vlm_processed: bool = False
    report_status: str = "abstain"
    report: Optional[Dict[str, Any]] = None
    contract_failures: List[str] = field(default_factory=list)
    decoding: Optional[Dict[str, Any]] = None
    
    @property
    def token_reduction(self) -> float:
        if self.tokens_total == 0:
            return 0.0
        return 1.0 - (self.tokens_used / self.tokens_total)


@dataclass
class VideoResult:
    """Result for a complete video."""
    video_path: str
    total_frames: int
    processed_frames: int
    event_frames: int
    frame_results: List[FrameResult]
    total_time: float
    fps: float
    
    @property
    def event_ratio(self) -> float:
        return self.event_frames / max(self.processed_frames, 1)
    
    @property
    def captions(self) -> List[str]:
        return [r.caption for r in self.frame_results if r.caption]


class EventVLM:
    """
    Event-VLM: Cascaded VLM framework for efficient video understanding.
    
    Three-stage pipeline:
    1. Event-Triggered Gating: Lightweight detector filters background frames
    2. Knowledge-Guided Token Pruning: Detector priors mask irrelevant tokens
    3. Context-Aware Generation: VLM generates hazard descriptions
    """
    
    def __init__(
        self,
        config: Optional[EventVLMConfig] = None,
        detector: Optional[str] = None,
        vlm: Optional[str] = None,
        device: str = "cuda",
        verbose: bool = False
    ):
        """
        Args:
            config: Full configuration object
            detector: Optional detector model override
            vlm: Optional VLM model override
            device: Target device
            verbose: Enable verbose logging
        """
        self.config = config or EventVLMConfig()
        self.device = device
        self.verbose = verbose
        
        # Override config with explicit parameters
        if detector:
            self.config.detector.model = detector
        if vlm:
            self.config.vlm.model = vlm
        
        # Initialize components
        self.detector = None
        self.pruner = None
        self.vlm = None
        self.prompting = None
        self.decoding_selector = None
        self.reporting_contract = None
        
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize all components."""
        if self._initialized:
            return
        
        logger.info("Initializing Event-VLM pipeline...")
        
        # Stage 1: Detector
        logger.info(f"Loading detector: {self.config.detector.model}")
        self.detector = get_detector(
            model_name=self.config.detector.model,
            conf_threshold=self.config.detector.conf_threshold,
            iou_threshold=self.config.detector.iou_threshold,
            hazard_classes=self.config.detector.hazard_classes,
            device=self.device
        )
        
        # Stage 2: Token Pruner
        logger.info("Initializing token pruner")
        self.pruner = TokenPruner(
            image_size=self.config.data.image_size,
            patch_size=14,  # ViT default
            alpha_base=self.config.pruning.alpha_base,
            beta=self.config.pruning.beta,
            min_tokens=self.config.pruning.min_tokens,
            preserve_cls_token=self.config.pruning.preserve_cls_token,
            shape_variance=self.config.pruning.shape_variance
        )
        
        # Stage 3: VLM
        logger.info(f"Loading VLM: {self.config.vlm.model}")
        self.vlm = LLaVAWrapper(
            model_name=self.config.vlm.model,
            quantization=self.config.vlm.quantization,
            device=self.device,
            max_new_tokens=self.config.vlm.max_new_tokens,
            temperature=self.config.vlm.temperature,
            do_sample=self.config.vlm.do_sample
        )
        
        # Hazard-Priority Prompting
        self.prompting = HazardPriorityPrompting()

        self.decoding_selector = EvidenceAwareFCSparseSelector(
            FCSparseConfig(
                enabled=self.config.decoding.enabled,
                budget=self.config.decoding.budget,
                min_keep=self.config.decoding.min_keep,
                sink_tokens=self.config.decoding.sink_tokens,
                recent_tokens=self.config.decoding.recent_tokens,
                preserve_evidence=self.config.decoding.preserve_evidence,
                dense_fallback=self.config.decoding.dense_fallback,
                chunk_count=self.config.decoding.chunk_count,
                dominant_chunks=tuple(self.config.decoding.dominant_chunks),
            )
        )
        self.reporting_contract = ReportingContract(
            ReportingPolicy(
                min_evidence_links=self.config.reporting.min_evidence_links,
                min_evidence_confidence=self.config.reporting.min_evidence_confidence,
                max_latency_ms=self.config.reporting.max_latency_ms,
            )
        )
        
        self._initialized = True
        logger.info("Event-VLM pipeline initialized")
    
    def process_frame(
        self,
        frame: np.ndarray,
        frame_idx: int = 0,
        timestamp: float = 0.0,
        force_vlm: bool = False
    ) -> FrameResult:
        """
        Process a single frame through the pipeline.
        
        Args:
            frame: Input frame (BGR or RGB)
            frame_idx: Frame index in video
            timestamp: Timestamp in seconds
            force_vlm: Force VLM processing regardless of trigger
            
        Returns:
            FrameResult with detections and optional caption
        """
        self.initialize()
        start_time = time.time()
        
        # Stage 1: Event-Triggered Gating
        detection_result = self.detector.detect(frame)
        
        result = FrameResult(
            frame_idx=frame_idx,
            timestamp=timestamp,
            is_event=detection_result.is_event,
            detections=detection_result.detections,
            hazard_level=detection_result.max_hazard_level
        )
        
        # Skip VLM if no event detected (unless forced or temporal gating is disabled).
        if self.config.gating.enabled and not detection_result.is_event and not force_vlm:
            result.processing_time = time.time() - start_time
            return result
        
        # Stage 2: Knowledge-Guided Token Pruning
        # First encode image to get visual tokens
        image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        visual_tokens = self.vlm.encode_image(image_pil)
        
        result.tokens_total = visual_tokens.shape[1]
        
        if self.config.pruning.enabled:
            pruned_tokens, pruning_result = self.pruner.prune(
                visual_tokens,
                detection_result.detections,
                return_mask=True
            )
            result.tokens_used = pruning_result.num_kept if pruning_result else result.tokens_total
        else:
            pruned_tokens = visual_tokens
            pruning_result = None
            result.tokens_used = result.tokens_total

        evidence_indices = []
        selection_evidence_indices = []
        if pruning_result is not None:
            evidence_indices = self._tensor_to_int_list(pruning_result.evidence_indices)
            selection_evidence_indices = self._selection_evidence_positions(
                pruning_result=pruning_result,
                pruned_tokens=pruned_tokens,
            )
        elif detection_result.detections:
            evidence_mask = self.pruner.create_mask(
                detection_result.detections,
                visual_tokens.device,
            )
            evidence_indices = self._tensor_to_int_list(
                evidence_mask.nonzero(as_tuple=True)[0]
            )
            selection_evidence_indices = list(evidence_indices)

        sparse_selection = self.decoding_selector.select(
            token_states=pruned_tokens,
            evidence_indices=selection_evidence_indices
        )
        result.decoding = sparse_selection.to_dict()
        
        # Stage 3: Context-Aware Generation
        detected_classes = [d.class_name for d in detection_result.detections]
        prompt_strategy = getattr(self.config.vlm, "prompt_strategy", "hazard_priority")

        if prompt_strategy == "standard":
            prompt = self.prompting.select_prompt(
                hazard_level="standard",
                detected_classes=detected_classes
            )
        elif prompt_strategy == "none":
            prompt = (
                "Describe what is happening in this surveillance footage. "
                "Focus on safety-relevant observations."
            )
        else:
            prompt = self.prompting(
                hazard_level=detection_result.max_hazard_level,
                detected_classes=detected_classes
            )
        
        vlm_output = self.vlm.generate(
            image=image_pil,
            prompt=prompt,
            pruned_tokens=pruned_tokens,
            sparse_selection=sparse_selection
        )
        
        result.caption = vlm_output.caption
        result.vlm_processed = True
        result.tokens_used = vlm_output.tokens_used or result.tokens_used
        result.decoding = vlm_output.decoding or result.decoding
        result.processing_time = time.time() - start_time

        if self.config.reporting.enabled:
            report = self.reporting_contract.build_frame_report(
                caption=result.caption,
                frame_idx=frame_idx,
                timestamp=timestamp,
                detections=detection_result.detections,
                latency_ms=result.processing_time * 1000.0,
                token_indices=evidence_indices,
                status="valid",
                metadata={"hazard_level": result.hazard_level},
            )
            validation = self.reporting_contract.validate(report)
            result.report_status = validation.resolved_status
            result.contract_failures = list(validation.failures)
            result.report = {
                "event_statement": report.event_statement,
                "status": validation.resolved_status,
                "requested_status": validation.requested_status,
                "evidence": [item.__dict__ for item in report.evidence],
                "failures": result.contract_failures,
                "latency_ms": report.latency_ms,
                "metadata": report.metadata,
            }
        else:
            result.report_status = "valid"
        
        return result

    @staticmethod
    def _tensor_to_int_list(tensor: Optional[torch.Tensor]) -> List[int]:
        if tensor is None:
            return []
        return [int(i) for i in tensor.detach().cpu().tolist()]

    @staticmethod
    def _selection_evidence_positions(
        *,
        pruning_result: Any,
        pruned_tokens: torch.Tensor,
    ) -> List[int]:
        evidence = set(EventVLM._tensor_to_int_list(pruning_result.evidence_indices))
        if not evidence:
            return []

        kept = EventVLM._tensor_to_int_list(pruning_result.kept_indices)
        offset = 0
        if pruned_tokens.dim() >= 2:
            token_count = int(pruned_tokens.shape[-2])
            if token_count == len(kept) + 1:
                offset = 1

        return [
            pos + offset
            for pos, original_idx in enumerate(kept)
            if original_idx in evidence
        ]
    
    def process_video(
        self,
        video_path: str,
        frame_rate: Optional[int] = None,
        max_frames: Optional[int] = None,
        callback: Optional[callable] = None
    ) -> VideoResult:
        """
        Process a complete video.
        
        Args:
            video_path: Path to video file
            frame_rate: Frames per second to extract (default: from config)
            max_frames: Maximum frames to process (default: from config)
            callback: Optional callback(frame_result) for each frame
            
        Returns:
            VideoResult with all frame results
        """
        self.initialize()
        start_time = time.time()
        
        frame_rate = frame_rate or self.config.data.frame_rate
        max_frames = max_frames or self.config.data.max_frames
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, int(video_fps / frame_rate))
        
        logger.info(f"Processing video: {video_path}")
        logger.info(f"Total frames: {total_frames}, Interval: {frame_interval}")
        
        frame_results = []
        frame_idx = 0
        processed = 0
        events = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample at specified frame rate
            if frame_idx % frame_interval != 0:
                frame_idx += 1
                continue
            
            timestamp = frame_idx / video_fps
            
            # Process frame
            result = self.process_frame(
                frame=frame,
                frame_idx=frame_idx,
                timestamp=timestamp
            )
            
            frame_results.append(result)
            processed += 1
            if result.is_event:
                events += 1
            
            if callback:
                callback(result)
            
            if self.verbose and processed % 10 == 0:
                logger.info(f"Processed {processed} frames, {events} events")
            
            # Check max frames
            if max_frames and processed >= max_frames:
                break
            
            frame_idx += 1
        
        cap.release()
        
        total_time = time.time() - start_time
        fps = processed / max(total_time, 1e-6)
        
        return VideoResult(
            video_path=video_path,
            total_frames=total_frames,
            processed_frames=processed,
            event_frames=events,
            frame_results=frame_results,
            total_time=total_time,
            fps=fps
        )
    
    def stream_video(
        self,
        video_path: str,
        frame_rate: Optional[int] = None
    ) -> Generator[FrameResult, None, None]:
        """
        Stream video processing as a generator.
        
        Args:
            video_path: Path to video file
            frame_rate: Frames per second to extract
            
        Yields:
            FrameResult for each processed frame
        """
        self.initialize()
        
        frame_rate = frame_rate or self.config.data.frame_rate
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video: {video_path}")
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = max(1, int(video_fps / frame_rate))
        
        frame_idx = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_interval != 0:
                    frame_idx += 1
                    continue
                
                timestamp = frame_idx / video_fps
                result = self.process_frame(frame, frame_idx, timestamp)
                
                yield result
                
                frame_idx += 1
        finally:
            cap.release()
    
    def benchmark(
        self,
        video_path: str,
        num_frames: int = 100
    ) -> Dict[str, float]:
        """
        Benchmark pipeline performance.
        
        Returns:
            Dict with timing metrics
        """
        self.initialize()
        
        cap = cv2.VideoCapture(video_path)
        frames = []
        for _ in range(num_frames):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        
        if not frames:
            raise IOError("No frames read from video")
        
        # Warm-up
        for frame in frames[:5]:
            self.process_frame(frame)
        
        # Benchmark
        times = {
            "detection": [],
            "encoding": [],
            "pruning": [],
            "generation": [],
            "total": []
        }
        
        for frame in frames:
            t0 = time.time()
            
            # Detection
            t1 = time.time()
            result = self.detector.detect(frame)
            times["detection"].append(time.time() - t1)
            
            if result.is_event:
                # Encoding
                t2 = time.time()
                image_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                tokens = self.vlm.encode_image(image_pil)
                times["encoding"].append(time.time() - t2)
                
                # Pruning
                t3 = time.time()
                pruned, _ = self.pruner.prune(tokens, result.detections)
                times["pruning"].append(time.time() - t3)
                
                # Generation
                t4 = time.time()
                prompt = self.prompting(result.max_hazard_level)
                self.vlm.generate(image_pil, prompt, pruned)
                times["generation"].append(time.time() - t4)
            
            times["total"].append(time.time() - t0)
        
        # Compute statistics
        metrics = {}
        for key, values in times.items():
            if values:
                metrics[f"{key}_mean"] = np.mean(values)
                metrics[f"{key}_std"] = np.std(values)
        
        metrics["fps"] = 1.0 / metrics.get("total_mean", 1.0)
        
        return metrics
