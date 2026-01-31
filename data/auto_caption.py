#!/usr/bin/env python3
"""
Automatic Captioning using Open-Source VLMs.
Generates pseudo-labels for UCF-Crime and XD-Violence datasets.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import time

import torch
import cv2
from tqdm import tqdm
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenSourceCaptioner:
    """
    Open-source VLM-based captioning for generating pseudo-labels.
    
    Supports:
    - InternVL-2 (recommended, Apache 2.0 license)
    - Qwen-VL-Chat (open weights)
    - CogVLM (open weights)
    - LLaVA-1.5 (open weights)
    """
    
    SUPPORTED_MODELS = {
        "internvl2-8b": {
            "hf_name": "OpenGVLab/InternVL2-8B",
            "type": "internvl",
            "params": "8B"
        },
        "internvl2-2b": {
            "hf_name": "OpenGVLab/InternVL2-2B",
            "type": "internvl",
            "params": "2B"
        },
        "qwen-vl-chat": {
            "hf_name": "Qwen/Qwen-VL-Chat",
            "type": "qwen",
            "params": "7B"
        },
        "cogvlm": {
            "hf_name": "THUDM/cogvlm-chat-hf",
            "type": "cogvlm",
            "params": "17B"
        },
        "llava-1.5-7b": {
            "hf_name": "liuhaotian/llava-v1.5-7b",
            "type": "llava",
            "params": "7B"
        }
    }
    
    def __init__(
        self,
        model_name: str = "internvl2-8b",
        device: str = "cuda",
        quantization: str = "4bit",
        max_new_tokens: int = 256
    ):
        self.model_name = model_name
        self.device = device
        self.quantization = quantization
        self.max_new_tokens = max_new_tokens
        
        self.model = None
        self.processor = None
        self.tokenizer = None
        self._loaded = False
    
    def load_model(self) -> None:
        """Load the specified VLM."""
        if self._loaded:
            return
        
        if self.model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        model_config = self.SUPPORTED_MODELS[self.model_name]
        logger.info(f"Loading {self.model_name} ({model_config['params']} params)...")
        
        if model_config["type"] == "internvl":
            self._load_internvl(model_config["hf_name"])
        elif model_config["type"] == "qwen":
            self._load_qwen(model_config["hf_name"])
        elif model_config["type"] == "llava":
            self._load_llava(model_config["hf_name"])
        else:
            raise ValueError(f"Unsupported model type: {model_config['type']}")
        
        self._loaded = True
        logger.info(f"Model loaded on {self.device}")
    
    def _load_internvl(self, hf_name: str) -> None:
        """Load InternVL2 model."""
        from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig
        
        if self.quantization == "4bit":
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        else:
            quant_config = None
        
        self.model = AutoModel.from_pretrained(
            hf_name,
            quantization_config=quant_config,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            hf_name,
            trust_remote_code=True
        )
    
    def _load_qwen(self, hf_name: str) -> None:
        """Load Qwen-VL model."""
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        
        if self.quantization == "4bit":
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16
            )
        else:
            quant_config = None
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            hf_name,
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            hf_name,
            quantization_config=quant_config,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
    
    def _load_llava(self, hf_name: str) -> None:
        """Load LLaVA model."""
        from llava.model.builder import load_pretrained_model
        from llava.mm_utils import get_model_name_from_path
        
        tokenizer, model, image_processor, _ = load_pretrained_model(
            model_path=hf_name,
            model_base=None,
            model_name=get_model_name_from_path(hf_name)
        )
        self.model = model
        self.tokenizer = tokenizer
        self.processor = image_processor
    
    def caption_image(
        self,
        image: Image.Image,
        prompt: Optional[str] = None
    ) -> str:
        """Generate caption for a single image."""
        self.load_model()
        
        if prompt is None:
            prompt = self._get_safety_prompt()
        
        model_config = self.SUPPORTED_MODELS[self.model_name]
        
        if model_config["type"] == "internvl":
            return self._caption_internvl(image, prompt)
        elif model_config["type"] == "qwen":
            return self._caption_qwen(image, prompt)
        elif model_config["type"] == "llava":
            return self._caption_llava(image, prompt)
        else:
            raise ValueError(f"Unsupported model type: {model_config['type']}")
    
    def _get_safety_prompt(self) -> str:
        """Get default safety analysis prompt."""
        return (
            "Analyze this surveillance footage and describe any safety-related events. "
            "If there is an anomaly or dangerous situation, describe:\n"
            "1. What type of incident is occurring\n"
            "2. Who or what is involved\n"
            "3. The severity of the situation\n"
            "4. Any recommended actions\n\n"
            "If the scene appears normal, briefly describe the scene."
        )
    
    def _caption_internvl(self, image: Image.Image, prompt: str) -> str:
        """Generate caption using InternVL."""
        pixel_values = self._preprocess_image_internvl(image)
        
        generation_config = dict(
            max_new_tokens=self.max_new_tokens,
            do_sample=False
        )
        
        response = self.model.chat(
            self.tokenizer,
            pixel_values,
            prompt,
            generation_config
        )
        return response
    
    def _preprocess_image_internvl(self, image: Image.Image):
        """Preprocess image for InternVL."""
        import torchvision.transforms as T
        from torchvision.transforms.functional import InterpolationMode
        
        IMAGENET_MEAN = (0.485, 0.456, 0.406)
        IMAGENET_STD = (0.229, 0.224, 0.225)
        
        transform = T.Compose([
            T.Resize((448, 448), interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
        
        pixel_values = transform(image).unsqueeze(0)
        return pixel_values.to(self.device, dtype=torch.float16)
    
    def _caption_qwen(self, image: Image.Image, prompt: str) -> str:
        """Generate caption using Qwen-VL."""
        # Save image temporarily for Qwen-VL
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            image.save(f.name)
            temp_path = f.name
        
        query = self.tokenizer.from_list_format([
            {'image': temp_path},
            {'text': prompt}
        ])
        
        response, _ = self.model.chat(self.tokenizer, query=query, history=None)
        
        # Cleanup
        import os
        os.unlink(temp_path)
        
        return response
    
    def _caption_llava(self, image: Image.Image, prompt: str) -> str:
        """Generate caption using LLaVA."""
        from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
        from llava.conversation import conv_templates
        from llava.mm_utils import tokenizer_image_token
        
        conv = conv_templates["v1"].copy()
        conv.append_message(conv.roles[0], DEFAULT_IMAGE_TOKEN + "\n" + prompt)
        conv.append_message(conv.roles[1], None)
        prompt_text = conv.get_prompt()
        
        input_ids = tokenizer_image_token(
            prompt_text,
            self.tokenizer,
            IMAGE_TOKEN_INDEX,
            return_tensors="pt"
        ).unsqueeze(0).to(self.device)
        
        image_tensor = self.processor.preprocess(image, return_tensors="pt")["pixel_values"]
        image_tensor = image_tensor.to(self.device, dtype=torch.float16)
        
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                images=image_tensor,
                max_new_tokens=self.max_new_tokens,
                use_cache=True
            )
        
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    def caption_video(
        self,
        video_path: str,
        sample_rate: int = 1,
        max_frames: int = 10
    ) -> List[Dict]:
        """Generate captions for key frames in a video."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_interval = max(1, int(fps / sample_rate))
        
        results = []
        frame_idx = 0
        sampled = 0
        
        while sampled < max_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to PIL
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Generate caption
            caption = self.caption_image(image)
            
            results.append({
                "frame_idx": frame_idx,
                "timestamp": frame_idx / fps,
                "caption": caption
            })
            
            sampled += 1
            frame_idx += frame_interval
        
        cap.release()
        return results


def generate_dataset_captions(
    data_dir: str,
    output_file: str,
    model_name: str = "internvl2-8b",
    max_videos: Optional[int] = None,
    sample_rate: int = 1,
    max_frames_per_video: int = 10
) -> None:
    """
    Generate captions for all videos in a dataset.
    
    Args:
        data_dir: Directory containing video files
        output_file: Output JSON file for captions
        model_name: VLM model to use
        max_videos: Maximum videos to process
        sample_rate: Frames per second to sample
        max_frames_per_video: Maximum frames per video
    """
    data_dir = Path(data_dir)
    captioner = OpenSourceCaptioner(model_name=model_name)
    
    # Find all videos
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
    videos = []
    for ext in video_extensions:
        videos.extend(data_dir.rglob(f'*{ext}'))
    
    if max_videos:
        videos = videos[:max_videos]
    
    logger.info(f"Processing {len(videos)} videos with {model_name}")
    
    all_captions = {}
    
    for video_path in tqdm(videos, desc="Captioning videos"):
        try:
            captions = captioner.caption_video(
                str(video_path),
                sample_rate=sample_rate,
                max_frames=max_frames_per_video
            )
            
            # Aggregate captions (use most detailed or first non-trivial)
            video_id = video_path.stem
            
            if captions:
                # Use the longest caption as representative
                best_caption = max(captions, key=lambda x: len(x["caption"]))
                all_captions[video_id] = {
                    "caption": best_caption["caption"],
                    "frame_captions": captions,
                    "video_path": str(video_path.relative_to(data_dir))
                }
                
        except Exception as e:
            logger.error(f"Error processing {video_path}: {e}")
            continue
    
    # Save results
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(all_captions, f, indent=2)
    
    logger.info(f"Saved {len(all_captions)} captions to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate captions using open-source VLMs")
    parser.add_argument(
        "--data-dir",
        type=str,
        required=True,
        help="Directory containing videos"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="captions.json",
        help="Output JSON file"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="internvl2-8b",
        choices=list(OpenSourceCaptioner.SUPPORTED_MODELS.keys()),
        help="VLM model to use"
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Maximum videos to process"
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=1,
        help="Frames per second to sample"
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=10,
        help="Maximum frames per video"
    )
    
    args = parser.parse_args()
    
    generate_dataset_captions(
        data_dir=args.data_dir,
        output_file=args.output,
        model_name=args.model,
        max_videos=args.max_videos,
        sample_rate=args.sample_rate,
        max_frames_per_video=args.max_frames
    )


if __name__ == "__main__":
    main()
