"""Model definitions for sentiment and emotion classification."""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Optional

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from .config import (
    get_intensity,
    get_business_insight,
    MIXED_EMOTION_THRESHOLD,
    EMOTION_KEYWORDS,
    SARCASM_PRIORITY_EMOTIONS,
)
from .sarcasm_detector import get_sarcasm_detector

TextList = Iterable[str]


def build_pipeline(max_features: int = 12000, ngram_range: Tuple[int, int] = (1, 2)) -> Pipeline:
    """Create a TF-IDF + Logistic Regression pipeline."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=max_features,
                    ngram_range=ngram_range,
                    min_df=2,
                    strip_accents="unicode",
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    C=2.0,
                ),
            ),
        ]
    )


@dataclass
class ModelArtifacts:
    sentiment_model: Pipeline
    emotion_model: Pipeline

    def save(self, sentiment_path: Path, emotion_path: Path) -> None:
        sentiment_path.parent.mkdir(parents=True, exist_ok=True)
        emotion_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.sentiment_model, sentiment_path)
        joblib.dump(self.emotion_model, emotion_path)

    @classmethod
    def load(cls, sentiment_path: Path, emotion_path: Path) -> "ModelArtifacts":
        sentiment = joblib.load(sentiment_path)
        emotion = joblib.load(emotion_path)
        return cls(sentiment_model=sentiment, emotion_model=emotion)


class SentimentEmotionModel:
    """Wrapper around two text classifiers for sentiment and emotion."""

    def __init__(self, artifacts: ModelArtifacts | None = None) -> None:
        self.artifacts = artifacts or ModelArtifacts(
            sentiment_model=build_pipeline(), emotion_model=build_pipeline()
        )

    @property
    def sentiment_model(self) -> Pipeline:
        return self.artifacts.sentiment_model

    @property
    def emotion_model(self) -> Pipeline:
        return self.artifacts.emotion_model

    def fit(self, texts: TextList, sentiment_labels: TextList, emotion_labels: TextList) -> "SentimentEmotionModel":
        self.sentiment_model.fit(texts, sentiment_labels)
        self.emotion_model.fit(texts, emotion_labels)
        return self

    def predict(self, texts: TextList) -> Dict[str, List[str]]:
        sentiments = self.sentiment_model.predict(texts)
        emotions = self.emotion_model.predict(texts)
        return {"sentiment": sentiments, "emotion": emotions}

    def predict_proba(self, texts: TextList) -> Dict[str, np.ndarray]:
        sentiment_probs = self.sentiment_model.predict_proba(texts)
        emotion_probs = self.emotion_model.predict_proba(texts)
        return {"sentiment": sentiment_probs, "emotion": emotion_probs}

    def predict_with_details(self, text: str) -> Dict:
        """
        Enhanced prediction with confidence, intensity, mixed emotions, sarcasm, and business insights.
        
        Returns:
            Dictionary containing:
            - sentiment: predicted sentiment
            - sentiment_confidence: confidence score
            - sentiment_intensity: low/medium/high
            - emotion: primary emotion
            - emotion_confidence: confidence score
            - emotion_intensity: low/medium/high
            - secondary_emotion: secondary emotion if mixed
            - is_mixed_emotion: boolean flag
            - sarcasm_detected: boolean flag for sarcasm
            - sarcasm_confidence: sarcasm confidence score
            - sarcasm_indicators: list of sarcasm signals
            - business_insight: actionable recommendation
            - explanation: natural language explanation
        """
        cleaned = text
        
        # Get predictions
        preds = self.predict([cleaned])
        probs = self.predict_proba([cleaned])
        
        sentiment = preds["sentiment"][0]
        emotion = preds["emotion"][0]
        
        # Get class lists
        sentiment_classes = list(self.sentiment_model.named_steps["clf"].classes_)
        emotion_classes = list(self.emotion_model.named_steps["clf"].classes_)
        
        # Get confidence scores
        sentiment_conf = float(probs["sentiment"][0][sentiment_classes.index(sentiment)])
        emotion_conf = float(probs["emotion"][0][emotion_classes.index(emotion)])
        
        # Get intensity levels
        sentiment_intensity = get_intensity(sentiment_conf)
        emotion_intensity = get_intensity(emotion_conf)
        
        # Detect mixed emotions
        emotion_probs_sorted = sorted(
            zip(emotion_classes, probs["emotion"][0]),
            key=lambda x: x[1],
            reverse=True
        )
        primary_emotion = emotion_probs_sorted[0][0]
        secondary_emotion = emotion_probs_sorted[1][0] if len(emotion_probs_sorted) > 1 else None
        secondary_conf = emotion_probs_sorted[1][1] if len(emotion_probs_sorted) > 1 else 0.0
        
        is_mixed = False
        if secondary_emotion and (emotion_probs_sorted[0][1] - secondary_conf) < MIXED_EMOTION_THRESHOLD:
            is_mixed = True
        
        # SARCASM DETECTION
        sarcasm_detector = get_sarcasm_detector()
        sarcasm_result = sarcasm_detector.detect(
            text=cleaned,
            sentiment=sentiment,
            emotion=emotion
        )
        
        # If sarcasm detected with high confidence, re-interpret sentiment
        original_sentiment = sentiment
        if sarcasm_result.is_sarcastic and sarcasm_result.confidence > 0.7:
            # Sarcasm often flips positive to negative
            if sentiment == "positive":
                # Check if we should override based on emotion
                if emotion in SARCASM_PRIORITY_EMOTIONS:
                    sentiment = "negative"
        
        # Get business insight
        insight = get_business_insight(emotion)
        
        # Generate natural language explanation (with sarcasm context)
        explanation = generate_explanation(
            text=cleaned,
            sentiment=sentiment,
            emotion=emotion,
            sentiment_conf=sentiment_conf,
            emotion_conf=emotion_conf,
            tokens_sentiment=self.explain(cleaned, task="sentiment", top_n=3),
            tokens_emotion=self.explain(cleaned, task="emotion", top_n=3),
            sarcasm_result=sarcasm_result,
            original_sentiment=original_sentiment if sentiment != original_sentiment else None,
        )
        
        return {
            "sentiment": sentiment,
            "sentiment_confidence": sentiment_conf,
            "sentiment_intensity": sentiment_intensity,
            "emotion": primary_emotion,
            "emotion_confidence": emotion_conf,
            "emotion_intensity": emotion_intensity,
            "secondary_emotion": secondary_emotion if is_mixed else None,
            "secondary_confidence": float(secondary_conf) if is_mixed else None,
            "is_mixed_emotion": is_mixed,
            "sarcasm_detected": sarcasm_result.is_sarcastic,
            "sarcasm_confidence": sarcasm_result.confidence,
            "sarcasm_indicators": sarcasm_result.indicators,
            "business_insight": insight,
            "explanation": explanation,
        }

    def explain(self, text: str, task: str = "sentiment", top_n: int = 6) -> List[Tuple[str, float]]:
        pipeline = self.sentiment_model if task == "sentiment" else self.emotion_model
        return explain_with_coefficients(text, pipeline, top_n=top_n)

    def save(self, model_dir: Path) -> None:
        sentiment_path = model_dir / "sentiment_model.joblib"
        emotion_path = model_dir / "emotion_model.joblib"
        self.artifacts.save(sentiment_path, emotion_path)

    @classmethod
    def load(cls, model_dir: Path) -> "SentimentEmotionModel":
        sentiment_path = model_dir / "sentiment_model.joblib"
        emotion_path = model_dir / "emotion_model.joblib"
        artifacts = ModelArtifacts.load(sentiment_path, emotion_path)
        return cls(artifacts=artifacts)


def explain_with_coefficients(text: str, pipeline: Pipeline, top_n: int = 6) -> List[Tuple[str, float]]:
    """Return token-level importance using linear model coefficients."""
    vectorizer: TfidfVectorizer = pipeline.named_steps["tfidf"]
    classifier: LogisticRegression = pipeline.named_steps["clf"]

    vector = vectorizer.transform([text])
    feature_names = vectorizer.get_feature_names_out()
    class_index = classifier.predict(vector)[0]
    class_id = list(classifier.classes_).index(class_index)
    coef = classifier.coef_[class_id]

    indices = vector.nonzero()[1]
    scores = [(feature_names[idx], coef[idx] * vector[0, idx]) for idx in indices]
    scores = sorted(scores, key=lambda pair: abs(pair[1]), reverse=True)
    return scores[:top_n]


def generate_explanation(
    text: str,
    sentiment: str,
    emotion: str,
    sentiment_conf: float,
    emotion_conf: float,
    tokens_sentiment: List[Tuple[str, float]],
    tokens_emotion: List[Tuple[str, float]],
    sarcasm_result=None,
    original_sentiment: str = None,
) -> str:
    """
    Generate a natural language explanation for the prediction.
    
    Args:
        text: Original text
        sentiment: Predicted sentiment
        emotion: Predicted emotion
        sentiment_conf: Sentiment confidence
        emotion_conf: Emotion confidence
        tokens_sentiment: Top influential tokens for sentiment
        tokens_emotion: Top influential tokens for emotion
        sarcasm_result: SarcasmResult object (optional)
        original_sentiment: Original sentiment before sarcasm adjustment (optional)
    
    Returns:
        Natural language explanation string
    """
    # Extract top keywords
    sentiment_keywords = [token for token, _ in tokens_sentiment[:3]]
    emotion_keywords = [token for token, _ in tokens_emotion[:3]]
    
    # Find matching emotion-specific keywords from config
    text_lower = text.lower()
    matched_keywords = []
    if emotion in EMOTION_KEYWORDS:
        for keyword in EMOTION_KEYWORDS[emotion]:
            if keyword in text_lower:
                matched_keywords.append(f"'{keyword}'")
    
    # Build explanation
    parts = []
    
    # Confidence level description
    conf_desc = "high confidence" if emotion_conf > 0.75 else "moderate confidence" if emotion_conf > 0.55 else "lower confidence"
    
    # Base explanation
    parts.append(f"The model detected {emotion.upper()} with {conf_desc} ({emotion_conf:.2%}).")
    
    # Keyword explanation
    if matched_keywords:
        keywords_str = ", ".join(matched_keywords[:3])
        parts.append(f"This is indicated by {emotion}-related expressions such as {keywords_str}.")
    elif emotion_keywords:
        keywords_str = ", ".join([f"'{k}'" for k in emotion_keywords])
        parts.append(f"Key indicators include: {keywords_str}.")
    
    # SARCASM EXPLANATION
    if sarcasm_result and sarcasm_result.is_sarcastic:
        sarcasm_conf_desc = "strong" if sarcasm_result.confidence > 0.7 else "moderate"
        parts.append(f"⚠️ {sarcasm_conf_desc.capitalize()} sarcasm detected ({sarcasm_result.confidence:.1%}).")
        
        # Explain sarcasm indicators
        if sarcasm_result.indicators:
            indicator_summary = ", ".join(sarcasm_result.indicators[:2])
            parts.append(f"Sarcasm signals: {indicator_summary}.")
        
        # Explain sentiment re-evaluation if it happened
        if original_sentiment and original_sentiment != sentiment:
            parts.append(
                f"Although surface-level analysis suggested {original_sentiment} sentiment, "
                f"sarcasm detection re-evaluated this as {sentiment} due to ironic language use."
            )
        else:
            parts.append(
                f"The {sentiment} sentiment interpretation accounts for the detected sarcasm, "
                f"recognizing that positive words may be used ironically to express negativity."
            )
    else:
        # Normal sentiment alignment (no sarcasm)
        if (sentiment == "positive" and emotion in ["joy", "satisfaction", "trust", "excitement", "gratitude", "relief"]) or \
           (sentiment == "negative" and emotion in ["anger", "frustration", "disappointment", "sadness", "fear", "anxiety", "confusion", "annoyance", "regret"]):
            parts.append(f"The {sentiment} sentiment aligns with the {emotion} emotion.")
    
    return " ".join(parts)

