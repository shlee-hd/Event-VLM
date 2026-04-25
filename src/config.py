"""
Configuration management for Event-VLM.
Uses Hydra/OmegaConf for hierarchical configuration.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
from omegaconf import OmegaConf


@dataclass
class HazardWeights:
    """Risk-sensitive loss weights for hazard classes."""
    critical: float = 3.0  # fire, smoke, collapse
    high: float = 2.0      # forklift, machinery
    standard: float = 1.0  # person, vehicle


@dataclass
class GatingConfig:
    """Configuration for temporal event-triggered gating."""
    enabled: bool = True


@dataclass
class DetectorConfig:
    """Configuration for Stage 1: Event-Triggered Gating."""
    model: str = "detr-l"  # detr-l, yolov8s, yolov8n
    pretrained: bool = True
    conf_threshold: float = 0.5
    iou_threshold: float = 0.45
    risk_weights: HazardWeights = field(default_factory=HazardWeights)
    
    # Hazard class taxonomy
    hazard_classes: Dict[str, List[str]] = field(default_factory=lambda: {
        "critical": ["fire", "smoke", "collapse", "explosion"],
        "high": ["forklift", "crane", "machinery", "fall"],
        "standard": ["person", "vehicle", "helmet", "vest"]
    })


@dataclass
class PruningConfig:
    """Configuration for Stage 2: Knowledge-Guided Token Pruning."""
    enabled: bool = True
    alpha_base: float = 1.2      # Base dilation factor
    beta: float = 0.5            # Adaptive dilation coefficient
    min_tokens: int = 64         # Minimum tokens to preserve
    preserve_cls_token: bool = True
    
    # Intraclass shape variance (precomputed from training data)
    shape_variance: Dict[str, float] = field(default_factory=lambda: {
        "fire": 0.42,
        "smoke": 0.38,
        "person": 0.12,
        "vehicle": 0.08,
        "forklift": 0.15,
        "default": 0.20
    })


@dataclass
class VLMConfig:
    """Configuration for Stage 3: VLM with Hazard-Priority Prompting."""
    model: str = "llava-1.5-7b"
    quantization: str = "4bit"  # 4bit, 8bit, none
    max_new_tokens: int = 256
    temperature: float = 0.2
    do_sample: bool = False
    
    # Prompt configuration
    prompt_strategy: str = "hazard_priority"  # hazard_priority, standard
    prompt_bank: Dict[str, str] = field(default_factory=lambda: {
        "critical": (
            "Analyze this safety-critical scene in detail. "
            "Identify the hazard type, potential causes, affected personnel, "
            "and recommended immediate actions. Focus on fire spread direction "
            "or structural integrity if applicable."
        ),
        "high": (
            "Describe this workplace safety incident. "
            "Identify the equipment involved, any personnel at risk, "
            "and safety protocol violations."
        ),
        "standard": (
            "Describe what is happening in this surveillance footage. "
            "Focus on any safety-related observations."
        )
    })


@dataclass
class DecodingConfig:
    """Configuration for evidence-aware sparse decoding."""
    enabled: bool = False
    budget: int = 128
    min_keep: int = 64
    sink_tokens: int = 4
    recent_tokens: int = 32
    preserve_evidence: bool = True
    dense_fallback: bool = True
    chunk_count: int = 8
    dominant_chunks: List[int] = field(default_factory=lambda: [0, 1])


@dataclass
class ReportingConfig:
    """Configuration for fail-closed evidence reporting."""
    enabled: bool = True
    min_evidence_links: int = 1
    min_evidence_confidence: float = 0.0
    max_latency_ms: Optional[float] = None


@dataclass
class DataConfig:
    """Configuration for datasets."""
    name: str = "ucf_crime"
    root_dir: str = "data/"
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    num_workers: int = 4
    
    # Video processing
    frame_rate: int = 1  # Extract 1 frame per second
    max_frames: int = 300
    image_size: int = 336  # LLaVA default


@dataclass
class TrainingConfig:
    """Configuration for training."""
    epochs: int = 50
    batch_size: int = 16
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    warmup_steps: int = 500
    gradient_accumulation: int = 4
    mixed_precision: str = "fp16"
    
    # Checkpointing
    save_dir: str = "checkpoints/"
    save_every: int = 5
    
    # Logging
    log_every: int = 100
    use_wandb: bool = True
    wandb_project: str = "event-vlm"


@dataclass
class AutoTuneConfig:
    """Configuration for Optuna auto-tuning."""
    n_trials: int = 100
    timeout: Optional[int] = None  # Hours
    study_name: str = "event_vlm_tuning"
    storage: Optional[str] = None  # SQLite path
    
    # Search space
    search_space: Dict[str, Any] = field(default_factory=lambda: {
        "lambda_crit": {"low": 2.0, "high": 5.0},
        "lambda_high": {"low": 1.5, "high": 3.0},
        "alpha_base": {"low": 1.1, "high": 1.5},
        "beta": {"low": 0.3, "high": 0.8},
        "conf_threshold": {"low": 0.3, "high": 0.7}
    })
    
    # Optimization objective
    objectives: List[str] = field(default_factory=lambda: ["auc", "fps"])
    objective_weights: List[float] = field(default_factory=lambda: [1.0, 0.5])


@dataclass
class EventVLMConfig:
    """Main configuration for Event-VLM."""
    gating: GatingConfig = field(default_factory=GatingConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    pruning: PruningConfig = field(default_factory=PruningConfig)
    vlm: VLMConfig = field(default_factory=VLMConfig)
    decoding: DecodingConfig = field(default_factory=DecodingConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    auto_tune: AutoTuneConfig = field(default_factory=AutoTuneConfig)
    
    # Device configuration
    device: str = "cuda"
    seed: int = 42


def load_config(config_path: str) -> EventVLMConfig:
    """Load configuration from YAML file with lightweight defaults composition."""
    config_file = Path(config_path)

    def _resolve_default_path(entry: Any, parent: Path) -> Optional[Path]:
        """Resolve a Hydra-style defaults entry into a YAML file path."""
        if entry == "_self_":
            return None

        if isinstance(entry, str):
            rel = entry
        elif isinstance(entry, dict):
            if len(entry) != 1:
                raise ValueError(f"Unsupported defaults entry in {config_file}: {entry}")
            group, value = next(iter(entry.items()))
            if value in (None, "_self_"):
                return None
            rel = f"{group}/{value}"
        else:
            raise ValueError(f"Unsupported defaults entry type in {config_file}: {entry!r}")

        if not rel.endswith(".yaml"):
            rel = f"{rel}.yaml"
        return parent / rel

    def _compose(path: Path):
        """Recursively compose config files listed under `defaults`."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        cfg = OmegaConf.load(path)
        defaults = cfg.pop("defaults", [])
        merged = OmegaConf.create()

        for entry in defaults:
            default_path = _resolve_default_path(entry, path.parent)
            if default_path is None:
                continue
            merged = OmegaConf.merge(merged, _compose(default_path))

        return OmegaConf.merge(merged, cfg)

    # Compose file + defaults first, then keep only schema-compatible keys.
    composed = _compose(config_file)
    composed_dict = OmegaConf.to_container(composed, resolve=True)
    allowed_keys = set(EventVLMConfig.__dataclass_fields__.keys())
    filtered = {
        key: value
        for key, value in (composed_dict or {}).items()
        if key in allowed_keys
    }

    schema = OmegaConf.structured(EventVLMConfig)
    merged = OmegaConf.merge(schema, filtered)
    return OmegaConf.to_object(merged)


def save_config(config: EventVLMConfig, path: str) -> None:
    """Save configuration to YAML file."""
    conf = OmegaConf.structured(config)
    OmegaConf.save(conf, path)
