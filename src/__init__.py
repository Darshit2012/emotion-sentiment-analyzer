"""Customer Emotion Analysis - Core Package

This package provides multi-dimensional emotion analysis combining:
- 18-emotion fine-grained classification
- Sentiment analysis (positive/negative/neutral)
- Sarcasm detection
- Explainable AI with keyword highlighting
- Business intelligence insights
"""

__version__ = "1.0.0"

from .model import SentimentEmotionModel
from .sarcasm_detector import SarcasmDetector, get_sarcasm_detector
from .preprocessing import preprocess_text, preprocess_series
from .config import ALL_EMOTIONS, EMOTION_GROUPS

__all__ = [
    "SentimentEmotionModel",
    "SarcasmDetector",
    "get_sarcasm_detector",
    "preprocess_text",
    "preprocess_series",
    "ALL_EMOTIONS",
    "EMOTION_GROUPS",
]
