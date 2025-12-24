"""Batch analysis utilities for multiple feedback entries."""
from typing import List, Dict
import pandas as pd
from collections import Counter
import numpy as np

from .config import get_emotion_group, EMOTION_GROUPS


class BatchAnalyzer:
    """Analyzes batch predictions to extract trends and insights."""
    
    def __init__(self, predictions: List[Dict]):
        """
        Initialize with list of prediction dictionaries.
        
        Args:
            predictions: List of dicts from model.predict_with_details()
        """
        self.predictions = predictions
        self.df = pd.DataFrame(predictions)
    
    def sentiment_distribution(self) -> Dict[str, float]:
        """Get sentiment distribution as percentages."""
        counts = self.df["sentiment"].value_counts()
        total = len(self.df)
        return {k: (v / total * 100) for k, v in counts.items()}
    
    def emotion_distribution(self) -> Dict[str, float]:
        """Get emotion distribution as percentages."""
        counts = self.df["emotion"].value_counts()
        total = len(self.df)
        return {k: (v / total * 100) for k, v in counts.items()}
    
    def dominant_emotion(self) -> str:
        """Get the most frequent emotion."""
        return self.df["emotion"].mode()[0] if len(self.df) > 0 else "unknown"
    
    def average_confidence(self) -> Dict[str, float]:
        """Get average confidence scores."""
        return {
            "sentiment": float(self.df["sentiment_confidence"].mean()),
            "emotion": float(self.df["emotion_confidence"].mean()),
        }
    
    def intensity_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get intensity distribution for sentiment and emotion."""
        return {
            "sentiment": self.df["sentiment_intensity"].value_counts().to_dict(),
            "emotion": self.df["emotion_intensity"].value_counts().to_dict(),
        }
    
    def emotion_group_distribution(self) -> Dict[str, float]:
        """Get distribution across emotion groups (positive/negative/neutral)."""
        self.df["emotion_group"] = self.df["emotion"].apply(get_emotion_group)
        counts = self.df["emotion_group"].value_counts()
        total = len(self.df)
        return {k: (v / total * 100) for k, v in counts.items()}
    
    def mixed_emotion_rate(self) -> float:
        """Get percentage of feedback with mixed emotions."""
        mixed_count = self.df["is_mixed_emotion"].sum()
        return (mixed_count / len(self.df) * 100) if len(self.df) > 0 else 0.0
    
    def sarcasm_rate(self) -> float:
        """Get percentage of feedback with detected sarcasm."""
        if "sarcasm_detected" not in self.df.columns:
            return 0.0
        sarcasm_count = self.df["sarcasm_detected"].sum()
        return (sarcasm_count / len(self.df) * 100) if len(self.df) > 0 else 0.0
    
    def sarcastic_feedback(self, threshold: float = 0.5) -> pd.DataFrame:
        """
        Get feedback with detected sarcasm.
        
        Args:
            threshold: Minimum sarcasm confidence to include
        
        Returns:
            DataFrame with sarcastic feedback
        """
        if "sarcasm_detected" not in self.df.columns:
            return pd.DataFrame()
        
        sarcastic = self.df[
            (self.df["sarcasm_detected"] == True) &
            (self.df["sarcasm_confidence"] >= threshold)
        ].copy()
        
        if len(sarcastic) > 0:
            return sarcastic[["text", "emotion", "sentiment", "sarcasm_confidence"]]
        return pd.DataFrame()
    
    def sarcasm_sentiment_correlation(self) -> Dict[str, float]:
        """
        Analyze correlation between sarcasm and sentiment.
        Returns percentage of sarcastic feedback in each sentiment category.
        """
        if "sarcasm_detected" not in self.df.columns:
            return {}
        
        correlation = {}
        for sentiment in ["positive", "negative", "neutral"]:
            sentiment_df = self.df[self.df["sentiment"] == sentiment]
            if len(sentiment_df) > 0:
                sarcasm_in_sentiment = sentiment_df["sarcasm_detected"].sum()
                pct = (sarcasm_in_sentiment / len(sentiment_df)) * 100
                correlation[sentiment] = pct
            else:
                correlation[sentiment] = 0.0
        
        return correlation
    
    def priority_breakdown(self) -> Dict[str, int]:
        """Get count of feedback by business priority level."""
        priorities = [pred.get("business_insight", {}).get("priority", "Unknown") 
                     for pred in self.predictions]
        return dict(Counter(priorities))
    
    def category_breakdown(self) -> Dict[str, int]:
        """Get count of feedback by business category."""
        categories = [pred.get("business_insight", {}).get("category", "Unknown") 
                     for pred in self.predictions]
        return dict(Counter(categories))
    
    def high_risk_feedback(self, threshold: float = 0.75) -> pd.DataFrame:
        """
        Identify high-risk feedback requiring immediate attention.
        
        Returns feedback with:
        - Negative emotions (anger, frustration, disappointment)
        - High confidence (> threshold)
        - Critical or High priority
        """
        high_risk = self.df[
            (self.df["emotion"].isin(["anger", "frustration", "disappointment", "regret"])) &
            (self.df["emotion_confidence"] > threshold)
        ].copy()
        
        return high_risk[["text", "emotion", "emotion_confidence", "sentiment"]] if len(high_risk) > 0 else pd.DataFrame()
    
    def positive_opportunities(self, threshold: float = 0.75) -> pd.DataFrame:
        """
        Identify positive feedback for leveraging.
        
        Returns feedback with:
        - Positive emotions (joy, satisfaction, gratitude, trust)
        - High confidence (> threshold)
        """
        positive = self.df[
            (self.df["emotion"].isin(["joy", "satisfaction", "gratitude", "trust", "excitement"])) &
            (self.df["emotion_confidence"] > threshold)
        ].copy()
        
        return positive[["text", "emotion", "emotion_confidence", "sentiment"]] if len(positive) > 0 else pd.DataFrame()
    
    def generate_summary_report(self) -> Dict:
        """Generate a comprehensive summary report."""
        total = len(self.df)
        
        # Overall sentiment
        sentiment_dist = self.sentiment_distribution()
        dominant_sentiment = max(sentiment_dist.items(), key=lambda x: x[1])[0] if sentiment_dist else "unknown"
        
        # Emotion insights
        emotion_dist = self.emotion_distribution()
        top_3_emotions = sorted(emotion_dist.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Risk assessment
        high_risk_count = len(self.high_risk_feedback())
        positive_opp_count = len(self.positive_opportunities())
        
        # Confidence metrics
        avg_conf = self.average_confidence()
        
        # Business priorities
        priority_counts = self.priority_breakdown()
        critical_count = priority_counts.get("Critical", 0)
        high_count = priority_counts.get("High", 0)
        
        # Sarcasm metrics
        sarcasm_pct = self.sarcasm_rate()
        sarcasm_correlation = self.sarcasm_sentiment_correlation()
        
        return {
            "total_feedback": total,
            "dominant_sentiment": dominant_sentiment,
            "sentiment_breakdown": sentiment_dist,
            "top_3_emotions": {k: v for k, v in top_3_emotions},
            "emotion_group_distribution": self.emotion_group_distribution(),
            "mixed_emotion_rate": self.mixed_emotion_rate(),
            "sarcasm_rate": sarcasm_pct,
            "sarcasm_sentiment_correlation": sarcasm_correlation,
            "average_confidence": avg_conf,
            "high_risk_count": high_risk_count,
            "positive_opportunity_count": positive_opp_count,
            "urgent_attention_needed": critical_count + high_count,
            "priority_breakdown": priority_counts,
            "category_breakdown": self.category_breakdown(),
        }
    
    def get_emotional_trend_text(self) -> str:
        """Generate a text summary of emotional trends."""
        summary = self.generate_summary_report()
        
        lines = [
            f"📊 **Batch Analysis Summary** ({summary['total_feedback']} feedbacks)",
            "",
            f"**Overall Sentiment**: {summary['dominant_sentiment'].capitalize()} dominant",
            "",
            "**Top 3 Emotions**:",
        ]
        
        for emotion, pct in summary['top_3_emotions'].items():
            lines.append(f"  - {emotion.capitalize()}: {pct:.1f}%")
        
        lines.append("")
        lines.append(f"**Mixed Emotions**: {summary['mixed_emotion_rate']:.1f}% of feedback")
        
        # Add sarcasm metrics if available
        if summary.get('sarcasm_rate', 0) > 0:
            lines.append(f"**Sarcasm Detected**: {summary['sarcasm_rate']:.1f}% of feedback")
            
            # Show sarcasm correlation with sentiment if available
            if summary.get('sarcasm_sentiment_correlation'):
                lines.append("  - Sarcasm in negative feedback: {:.1f}%".format(
                    summary['sarcasm_sentiment_correlation'].get('negative', 0)
                ))
        
        lines.append("")
        lines.append("**Emotion Groups**:")
        
        for group, pct in summary['emotion_group_distribution'].items():
            lines.append(f"  - {group.replace('_', ' ').title()}: {pct:.1f}%")
        
        lines.append("")
        lines.append("**Business Actions**:")
        lines.append(f"  - ⚠️ High Risk: {summary['high_risk_count']} items")
        lines.append(f"  - ✅ Positive Opportunities: {summary['positive_opportunity_count']} items")
        lines.append(f"  - 🚨 Urgent Attention: {summary['urgent_attention_needed']} items")
        
        return "\n".join(lines)
