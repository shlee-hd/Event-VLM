"""
Event-VLM: Scalable Vision-Language Models for Real-Time Industrial Surveillance
"""

__version__ = "0.1.0"
__all__ = ["EventVLM"]


def __getattr__(name):
    """Lazy import heavy modules to avoid hard dependency at package import time."""
    if name == "EventVLM":
        from src.pipeline.event_vlm import EventVLM
        return EventVLM
    raise AttributeError(f"module 'src' has no attribute '{name}'")
