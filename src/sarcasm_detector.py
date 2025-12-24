"""
Sarcasm Detection Module

A lightweight rule-based sarcasm detector designed for customer feedback analysis.
Uses pattern matching, contrast detection, and sentiment polarity analysis.

This is NOT a deep learning model - it's a practical heuristic system suitable
for final-year projects, focusing on explainability and clarity.
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class SarcasmResult:
    """Container for sarcasm detection results."""
    is_sarcastic: bool
    confidence: float
    indicators: List[str]  # List of detected sarcasm indicators
    explanation: str
    

class SarcasmDetector:
    """
    Rule-based sarcasm detector using multiple heuristic approaches.
    
    Detection Strategies:
    1. Contrast phrases (positive words with negative context)
    2. Excessive punctuation patterns
    3. Quotation marks around positive words
    4. Known sarcastic expressions
    5. Sentiment-emotion polarity mismatch
    """
    
    # Known sarcastic phrases and expressions
    SARCASTIC_PHRASES = [
        r"great job",
        r"well done",
        r"thanks a lot",
        r"oh wonderful",
        r"oh great",
        r"just wonderful",
        r"just perfect",
        r"brilliant idea",
        r"genius",
        r"fantastic",
        r"amazing work",
        r"real smart",
        r"very helpful",
        r"so helpful",
        r"love it when",
        r"really appreciate",
        r"couldn't be better",
    ]
    
    # Negative context indicators (words that suggest complaint/problem)
    NEGATIVE_CONTEXT = [
        "terrible", "awful", "horrible", "worst", "useless", "broken", "failed",
        "disaster", "nightmare", "unacceptable", "ridiculous", "pathetic",
        "waste", "never", "disappointed", "frustrated", "angry", "furious",
        "can't believe", "seriously", "joke", "kidding"
    ]
    
    # Positive surface words (might be used sarcastically)
    POSITIVE_SURFACE = [
        "great", "wonderful", "excellent", "perfect", "amazing", "fantastic",
        "brilliant", "awesome", "outstanding", "superb", "lovely", "nice",
        "thanks", "thank", "appreciate", "love", "enjoy"
    ]
    
    # Intensifiers that might indicate sarcasm when combined with positive words
    SARCASTIC_INTENSIFIERS = [
        "really", "so", "very", "such", "totally", "absolutely", "definitely",
        "surely", "clearly", "obviously", "just"
    ]
    
    def __init__(self):
        """Initialize the sarcasm detector with compiled patterns."""
        self.sarcastic_phrase_patterns = [
            re.compile(r'\b' + phrase + r'\b', re.IGNORECASE) 
            for phrase in self.SARCASTIC_PHRASES
        ]
    
    def detect(self, text: str, sentiment: str = None, emotion: str = None) -> SarcasmResult:
        """
        Detect sarcasm in the given text.
        
        Args:
            text: Input text to analyze
            sentiment: Predicted sentiment (optional, helps with polarity mismatch detection)
            emotion: Predicted emotion (optional, helps with emotion-based detection)
        
        Returns:
            SarcasmResult object with detection results
        """
        text_lower = text.lower()
        indicators = []
        confidence_scores = []
        
        # 1. Check for known sarcastic phrases
        phrase_score, phrase_indicators = self._detect_sarcastic_phrases(text_lower)
        if phrase_score > 0:
            confidence_scores.append(phrase_score)
            indicators.extend(phrase_indicators)
        
        # 2. Check for contrast (positive words + negative context)
        contrast_score, contrast_indicators = self._detect_contrast(text_lower)
        if contrast_score > 0:
            confidence_scores.append(contrast_score)
            indicators.extend(contrast_indicators)
        
        # 3. Check for excessive punctuation
        punct_score, punct_indicators = self._detect_excessive_punctuation(text)
        if punct_score > 0:
            confidence_scores.append(punct_score)
            indicators.extend(punct_indicators)
        
        # 4. Check for quoted positive words (e.g., "great" service)
        quote_score, quote_indicators = self._detect_quoted_positives(text)
        if quote_score > 0:
            confidence_scores.append(quote_score)
            indicators.extend(quote_indicators)
        
        # 5. Check for sentiment-emotion mismatch (if provided)
        if sentiment and emotion:
            mismatch_score, mismatch_indicators = self._detect_polarity_mismatch(
                sentiment, emotion
            )
            if mismatch_score > 0:
                confidence_scores.append(mismatch_score)
                indicators.extend(mismatch_indicators)
        
        # Calculate overall confidence
        if confidence_scores:
            # Average of detected indicators, with bonus for multiple signals
            base_confidence = sum(confidence_scores) / len(confidence_scores)
            multi_indicator_bonus = min(0.15 * (len(confidence_scores) - 1), 0.3)
            final_confidence = min(base_confidence + multi_indicator_bonus, 0.95)
            is_sarcastic = final_confidence > 0.5
        else:
            is_sarcastic = False
            final_confidence = 0.0
        
        # Generate explanation
        explanation = self._generate_explanation(indicators, is_sarcastic)
        
        return SarcasmResult(
            is_sarcastic=is_sarcastic,
            confidence=final_confidence,
            indicators=indicators,
            explanation=explanation
        )
    
    def _detect_sarcastic_phrases(self, text_lower: str) -> Tuple[float, List[str]]:
        """Detect known sarcastic expressions."""
        indicators = []
        for pattern in self.sarcastic_phrase_patterns:
            match = pattern.search(text_lower)
            if match:
                indicators.append(f"sarcastic phrase: '{match.group()}'")
        
        if indicators:
            # Higher confidence for explicit sarcastic phrases
            return 0.75, indicators
        return 0.0, []
    
    def _detect_contrast(self, text_lower: str) -> Tuple[float, List[str]]:
        """
        Detect contrast between positive surface words and negative context.
        Classic sarcasm pattern: positive words in negative situations.
        """
        positive_found = []
        negative_found = []
        
        # Find positive words
        for word in self.POSITIVE_SURFACE:
            if re.search(r'\b' + word + r'\b', text_lower):
                positive_found.append(word)
        
        # Find negative context
        for word in self.NEGATIVE_CONTEXT:
            if re.search(r'\b' + word + r'\b', text_lower):
                negative_found.append(word)
        
        # Check for intensifier + positive (e.g., "so helpful")
        intensified_positives = []
        for intensifier in self.SARCASTIC_INTENSIFIERS:
            for positive in self.POSITIVE_SURFACE:
                pattern = r'\b' + intensifier + r'\s+' + positive + r'\b'
                if re.search(pattern, text_lower):
                    intensified_positives.append(f"{intensifier} {positive}")
        
        indicators = []
        score = 0.0
        
        # If positive words appear with negative context words
        if positive_found and negative_found:
            indicators.append(f"contrast: positive words ({', '.join(positive_found[:2])}) with negative context ({', '.join(negative_found[:2])})")
            score = 0.7
        
        # Intensified positives are often sarcastic even without explicit negative words
        if intensified_positives:
            indicators.append(f"intensified positive: '{intensified_positives[0]}'")
            score = max(score, 0.65)
        
        return score, indicators
    
    def _detect_excessive_punctuation(self, text: str) -> Tuple[float, List[str]]:
        """
        Detect excessive exclamation/question marks.
        Multiple punctuation marks often indicate sarcasm or exaggeration.
        """
        indicators = []
        
        # Multiple exclamation marks
        if re.search(r'!{2,}', text):
            indicators.append("excessive exclamation marks")
        
        # Multiple question marks
        if re.search(r'\?{2,}', text):
            indicators.append("excessive question marks")
        
        # Mixed punctuation
        if re.search(r'[!?]{3,}', text):
            indicators.append("mixed excessive punctuation")
        
        if indicators:
            return 0.55, indicators
        return 0.0, []
    
    def _detect_quoted_positives(self, text: str) -> Tuple[float, List[str]]:
        """
        Detect positive words in quotation marks.
        Quotes around positive words often indicate sarcasm (e.g., "great" service).
        """
        indicators = []
        
        # Check for quoted words
        quoted_pattern = r'["\'](\w+)["\']'
        matches = re.finditer(quoted_pattern, text.lower())
        
        for match in matches:
            word = match.group(1)
            if word in self.POSITIVE_SURFACE:
                indicators.append(f"quoted positive word: '{word}'")
        
        if indicators:
            return 0.7, indicators
        return 0.0, []
    
    def _detect_polarity_mismatch(self, sentiment: str, emotion: str) -> Tuple[float, List[str]]:
        """
        Detect mismatch between sentiment and emotion that might indicate sarcasm.
        E.g., positive sentiment with anger emotion.
        """
        indicators = []
        
        # Define emotion groups
        negative_emotions = [
            "anger", "frustration", "disappointment", "sadness", 
            "fear", "anxiety", "annoyance", "regret"
        ]
        positive_emotions = [
            "joy", "satisfaction", "trust", "excitement", "gratitude", "relief"
        ]
        
        # Positive sentiment with negative emotion (rare, might be sarcasm)
        if sentiment == "positive" and emotion in negative_emotions:
            indicators.append(f"polarity mismatch: positive sentiment with {emotion} emotion")
            return 0.6, indicators
        
        return 0.0, []
    
    def _generate_explanation(self, indicators: List[str], is_sarcastic: bool) -> str:
        """Generate a human-readable explanation of the sarcasm detection."""
        if not is_sarcastic:
            return "No sarcasm detected. Text appears straightforward."
        
        if len(indicators) == 0:
            return "Low sarcasm signals detected."
        
        explanation_parts = ["Sarcasm detected based on:"]
        for i, indicator in enumerate(indicators[:3], 1):  # Show top 3 indicators
            explanation_parts.append(f"{i}. {indicator.capitalize()}")
        
        return " ".join(explanation_parts)


# Singleton instance for easy import
_detector_instance = None

def get_sarcasm_detector() -> SarcasmDetector:
    """Get or create the singleton sarcasm detector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = SarcasmDetector()
    return _detector_instance
