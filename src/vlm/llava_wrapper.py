"""
LLaVA Wrapper for Stage 3: VLM Integration.
Supports 4-bit quantization for efficient inference.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
import logging

import torch
import torch.nn as nn
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class VLMOutput:
    """Output from VLM generation."""
    caption: str
    hazard_level: str
    confidence: float
    tokens_used: int
    generation_time: float


class LLaVAWrapper:
    """
    LLaVA-1.5 wrapper with 4-bit quantization support.
    
    Integrates with token pruning by accepting pre-pruned visual tokens.
    """
    
    SUPPORTED_MODELS = [
        "llava-1.5-7b",
        "llava-1.5-13b",
        "llava-1.6-vicuna-7b",
        "llava-1.6-vicuna-13b",
    ]
    
    def __init__(
        self,
        model_name: str = "llava-1.5-7b",
        quantization: str = "4bit",
        device: str = "cuda",
        max_new_tokens: int = 256,
        temperature: float = 0.2,
        do_sample: bool = False,
        torch_dtype: torch.dtype = torch.float16
    ):
        """
        Args:
            model_name: LLaVA model variant
            quantization: Quantization mode (4bit, 8bit, none)
            device: Target device
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            do_sample: Whether to sample or use greedy decoding
            torch_dtype: Torch dtype for model
        """
        self.model_name = model_name
        self.quantization = quantization
        self.device = device
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.do_sample = do_sample
        self.torch_dtype = torch_dtype
        
        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.vision_tower = None
        
        self._loaded = False
    
    def load_model(self) -> None:
        """Load LLaVA model with optional quantization."""
        if self._loaded:
            return
        
        try:
            from transformers import AutoTokenizer, BitsAndBytesConfig
            from llava.model.builder import load_pretrained_model
            from llava.mm_utils import get_model_name_from_path
            
            # Model path mapping
            model_paths = {
                "llava-1.5-7b": "liuhaotian/llava-v1.5-7b",
                "llava-1.5-13b": "liuhaotian/llava-v1.5-13b",
                "llava-1.6-vicuna-7b": "liuhaotian/llava-v1.6-vicuna-7b",
                "llava-1.6-vicuna-13b": "liuhaotian/llava-v1.6-vicuna-13b",
            }
            
            model_path = model_paths.get(self.model_name)
            if not model_path:
                raise ValueError(f"Unknown model: {self.model_name}")
            
            # Quantization config
            if self.quantization == "4bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=self.torch_dtype,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif self.quantization == "8bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True
                )
            else:
                quantization_config = None
            
            # Load model
            logger.info(f"Loading {self.model_name} with {self.quantization} quantization...")
            
            tokenizer, model, image_processor, context_len = load_pretrained_model(
                model_path=model_path,
                model_base=None,
                model_name=get_model_name_from_path(model_path),
                device=self.device,
                quantization_config=quantization_config
            )
            
            self.model = model
            self.tokenizer = tokenizer
            self.image_processor = image_processor
            self.context_len = context_len
            self.vision_tower = model.get_vision_tower()
            
            self._loaded = True
            logger.info(f"Model loaded successfully on {self.device}")
            
        except ImportError as e:
            logger.error(f"Failed to import LLaVA: {e}")
            logger.error("Install with: pip install llava")
            raise
    
    def encode_image(self, image: Union[np.ndarray, Image.Image]) -> torch.Tensor:
        """
        Encode image to visual tokens.
        
        Args:
            image: Input image (numpy array or PIL Image)
            
        Returns:
            Visual tokens [1, L, D]
        """
        self.load_model()
        
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Process image
        image_tensor = self.image_processor.preprocess(
            image,
            return_tensors="pt"
        )["pixel_values"]
        
        image_tensor = image_tensor.to(
            device=self.device,
            dtype=self.torch_dtype
        )
        
        # Get visual features
        with torch.no_grad():
            image_features = self.vision_tower(image_tensor)
        
        return image_features
    
    def generate(
        self,
        image: Union[np.ndarray, Image.Image],
        prompt: str,
        pruned_tokens: Optional[torch.Tensor] = None
    ) -> VLMOutput:
        """
        Generate caption for image.
        
        Args:
            image: Input image
            prompt: Text prompt
            pruned_tokens: Optional pre-pruned visual tokens
            
        Returns:
            VLMOutput with generated caption
        """
        import time
        self.load_model()
        
        start_time = time.time()
        
        # Encode image if tokens not provided
        if pruned_tokens is None:
            image_features = self.encode_image(image)
        else:
            image_features = pruned_tokens
        
        tokens_used = image_features.shape[1] if image_features.dim() > 1 else 0
        
        # Prepare prompt
        full_prompt = self._format_prompt(prompt)
        
        # Tokenize
        input_ids = self.tokenizer(
            full_prompt,
            return_tensors="pt"
        ).input_ids.to(self.device)
        
        # Generate
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                images=image_features if pruned_tokens is None else None,
                image_features=pruned_tokens,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=self.do_sample,
                use_cache=True
            )
        
        # Decode
        caption = self.tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True
        )
        
        # Remove prompt from output
        caption = caption.replace(full_prompt, "").strip()
        
        generation_time = time.time() - start_time
        
        return VLMOutput(
            caption=caption,
            hazard_level="unknown",  # Set by caller
            confidence=1.0,
            tokens_used=tokens_used,
            generation_time=generation_time
        )
    
    def _format_prompt(self, prompt: str) -> str:
        """Format prompt for LLaVA."""
        return f"USER: <image>\n{prompt}\nASSISTANT:"
    
    def get_vision_tower_config(self) -> Dict[str, Any]:
        """Get vision tower configuration."""
        self.load_model()
        config = self.vision_tower.config
        return {
            "hidden_size": config.hidden_size,
            "image_size": config.image_size,
            "patch_size": config.patch_size,
            "num_patches": (config.image_size // config.patch_size) ** 2
        }


class MockLLaVAWrapper(LLaVAWrapper):
    """
    Mock LLaVA wrapper for testing without GPU.
    Returns dummy outputs for development and unit testing.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._loaded = True  # Skip actual loading
    
    def load_model(self) -> None:
        pass  # No-op
    
    def encode_image(self, image: Union[np.ndarray, Image.Image]) -> torch.Tensor:
        # Return dummy tokens [1, 576, 4096]
        return torch.randn(1, 576, 4096)
    
    def generate(
        self,
        image: Union[np.ndarray, Image.Image],
        prompt: str,
        pruned_tokens: Optional[torch.Tensor] = None
    ) -> VLMOutput:
        tokens_used = pruned_tokens.shape[1] if pruned_tokens is not None else 576
        
        return VLMOutput(
            caption="[Mock] A worker is performing a task in an industrial setting.",
            hazard_level="standard",
            confidence=0.95,
            tokens_used=tokens_used,
            generation_time=0.1
        )
