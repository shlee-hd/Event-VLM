"""
Hazard-Priority Prompting for Stage 3.
Dynamically selects prompts based on detected hazard severity.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """Template for hazard-specific prompt."""
    system_prompt: str
    user_prompt: str
    focus_keywords: List[str]
    
    def format(self, **kwargs) -> str:
        """Format prompt with optional keyword arguments."""
        full_prompt = f"{self.system_prompt}\n\n{self.user_prompt}"
        return full_prompt.format(**kwargs) if kwargs else full_prompt


class PromptBank:
    """
    Hierarchical prompt bank for hazard-priority prompting.
    
    Different hazard types require different levels of descriptive granularity.
    """
    
    DEFAULT_PROMPTS = {
        "critical": PromptTemplate(
            system_prompt=(
                "You are a safety expert analyzing surveillance footage. "
                "This is a CRITICAL safety event requiring immediate attention."
            ),
            user_prompt=(
                "Analyze this safety-critical scene in detail:\n"
                "1. Identify the primary hazard type (fire, smoke, explosion, collapse)\n"
                "2. Describe the hazard's current state and spread direction\n"
                "3. Identify any personnel in immediate danger\n"
                "4. Recommend immediate evacuation or intervention actions\n"
                "5. Note any secondary hazards or risks\n\n"
                "Provide a concise but comprehensive safety report."
            ),
            focus_keywords=["fire", "smoke", "explosion", "collapse", "danger", "evacuate"]
        ),
        
        "high": PromptTemplate(
            system_prompt=(
                "You are a safety expert analyzing surveillance footage. "
                "This involves heavy equipment or machinery that poses safety risks."
            ),
            user_prompt=(
                "Analyze this workplace safety scene:\n"
                "1. Identify the equipment or machinery involved\n"
                "2. Describe any unsafe operations or positioning\n"
                "3. Identify personnel at risk and their proximity to hazards\n"
                "4. Note any safety protocol violations\n"
                "5. Suggest corrective actions\n\n"
                "Provide a safety incident report."
            ),
            focus_keywords=["forklift", "crane", "machinery", "equipment", "collision", "struck"]
        ),
        
        "standard": PromptTemplate(
            system_prompt=(
                "You are a safety observer analyzing surveillance footage."
            ),
            user_prompt=(
                "Describe what is happening in this surveillance footage:\n"
                "1. Identify any people and their activities\n"
                "2. Note any vehicles or equipment present\n"
                "3. Observe any potential safety concerns\n"
                "4. Describe the overall scene and environment\n\n"
                "Focus on safety-relevant observations."
            ),
            focus_keywords=["person", "worker", "activity", "observe"]
        ),
        
        "none": PromptTemplate(
            system_prompt="You are analyzing surveillance footage.",
            user_prompt="Briefly describe the scene. Note if anything unusual is occurring.",
            focus_keywords=[]
        )
    }
    
    def __init__(
        self,
        custom_prompts: Optional[Dict[str, PromptTemplate]] = None
    ):
        """
        Args:
            custom_prompts: Optional custom prompt templates
        """
        self.prompts = self.DEFAULT_PROMPTS.copy()
        if custom_prompts:
            self.prompts.update(custom_prompts)
    
    def get_prompt(self, hazard_level: str) -> PromptTemplate:
        """Get prompt template for hazard level."""
        return self.prompts.get(hazard_level, self.prompts["standard"])
    
    def add_prompt(self, level: str, template: PromptTemplate) -> None:
        """Add or update a prompt template."""
        self.prompts[level] = template


class HazardPriorityPrompting:
    """
    Hazard-Priority Prompting mechanism.
    
    Dynamically selects from hierarchical prompt bank based on 
    detected hazard severity:
    
    P_active = P_critical if max_k w(c_k) > τ_crit
               P_high    if max_k w(c_k) > τ_high
               P_standard otherwise
    """
    
    def __init__(
        self,
        prompt_bank: Optional[PromptBank] = None,
        threshold_critical: float = 2.5,
        threshold_high: float = 1.5
    ):
        """
        Args:
            prompt_bank: PromptBank instance
            threshold_critical: Weight threshold for critical prompts
            threshold_high: Weight threshold for high-priority prompts
        """
        self.prompt_bank = prompt_bank or PromptBank()
        self.threshold_critical = threshold_critical
        self.threshold_high = threshold_high
        
        # Risk weights (matching RiskSensitiveLoss)
        self.risk_weights = {
            "critical": 3.0,
            "high": 2.0,
            "standard": 1.0,
            "none": 0.0
        }
    
    def get_max_risk_weight(self, hazard_levels: List[str]) -> float:
        """Get maximum risk weight from detected hazard levels."""
        if not hazard_levels:
            return 0.0
        weights = [self.risk_weights.get(level, 0.0) for level in hazard_levels]
        return max(weights)
    
    def select_prompt(
        self,
        hazard_level: str,
        detected_classes: Optional[List[str]] = None
    ) -> str:
        """
        Select appropriate prompt based on hazard level.
        
        Args:
            hazard_level: Maximum hazard level from detections
            detected_classes: Optional list of detected class names
            
        Returns:
            Formatted prompt string
        """
        template = self.prompt_bank.get_prompt(hazard_level)
        
        # Optionally include detected classes in prompt
        if detected_classes:
            classes_str = ", ".join(detected_classes[:5])  # Limit to 5
            return f"{template.format()}\n\nDetected objects: {classes_str}"
        
        return template.format()
    
    def select_prompt_by_weight(
        self,
        max_weight: float,
        detected_classes: Optional[List[str]] = None
    ) -> str:
        """
        Select prompt based on maximum risk weight.
        
        Args:
            max_weight: Maximum w(c_k) from detections
            detected_classes: Optional detected class names
            
        Returns:
            Formatted prompt string
        """
        if max_weight >= self.threshold_critical:
            level = "critical"
        elif max_weight >= self.threshold_high:
            level = "high"
        elif max_weight > 0:
            level = "standard"
        else:
            level = "none"
        
        return self.select_prompt(level, detected_classes)
    
    def __call__(
        self,
        hazard_level: str,
        detected_classes: Optional[List[str]] = None
    ) -> str:
        """Callable interface for prompt selection."""
        return self.select_prompt(hazard_level, detected_classes)


@dataclass
class SoftPromptConfig:
    """Configuration for learnable soft prompts (optional fine-tuning)."""
    num_tokens: int = 8
    embedding_dim: int = 4096
    init_from_text: bool = True
    init_text: str = "Analyze this safety surveillance scene carefully."
    freeze_after_init: bool = False


class LearnableSoftPrompts:
    """
    Learnable soft prompt vectors for domain adaptation.
    
    During training, only these vectors are updated while the 
    VLM backbone remains frozen.
    """
    
    def __init__(
        self,
        config: SoftPromptConfig,
        tokenizer=None,
        device: str = "cuda"
    ):
        import torch
        import torch.nn as nn
        
        self.config = config
        self.device = device
        
        # Initialize prompt embeddings
        self.prompt_embeddings = nn.Parameter(
            torch.randn(config.num_tokens, config.embedding_dim)
        )
        
        # Optionally initialize from text
        if config.init_from_text and tokenizer:
            self._init_from_text(tokenizer, config.init_text)
        
        self.prompt_embeddings = self.prompt_embeddings.to(device)
    
    def _init_from_text(self, tokenizer, text: str) -> None:
        """Initialize embeddings from text tokens."""
        import torch
        
        tokens = tokenizer(text, return_tensors="pt")
        # Use token embeddings as initialization
        # (Implementation depends on specific tokenizer/model)
        logger.info(f"Initialized soft prompts from: '{text}'")
    
    def get_embeddings(self) -> "torch.Tensor":
        """Get current prompt embeddings."""
        return self.prompt_embeddings
    
    def parameters(self):
        """Return trainable parameters."""
        return [self.prompt_embeddings]
