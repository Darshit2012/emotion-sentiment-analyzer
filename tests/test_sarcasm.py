"""
Test script for sarcasm detection functionality.
Tests both the sarcasm detector independently and its integration with the full system.
"""

import sys
from pathlib import Path

# Add src to path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from sarcasm_detector import SarcasmDetector
from model import SentimentEmotionModel
from preprocessing import preprocess_text, ensure_nltk_resources

def test_sarcasm_detector():
    """Test the standalone sarcasm detector."""
    print("\n" + "="*80)
    print("TESTING STANDALONE SARCASM DETECTOR")
    print("="*80)
    
    detector = SarcasmDetector()
    
    # Test cases: (text, expected_sarcastic, description)
    test_cases = [
        # Clearly sarcastic
        ("Great job breaking my order again!", True, "Sarcastic phrase with negative context"),
        ("Oh wonderful, another delay. Thanks a lot!", True, "Multiple sarcastic phrases"),
        ("Really helpful customer service!!!", True, "Intensified positive with excessive punctuation"),
        ("Your 'great' support team ignored me for days", True, "Quoted positive word"),
        ("Yeah, so helpful, leaving me without any solution", True, "Contrast: positive word + negative context"),
        
        # Not sarcastic
        ("Thank you so much! This is amazing!", False, "Genuine enthusiasm"),
        ("Really happy with the quality and service", False, "Genuine positive feedback"),
        ("The product is okay, nothing special", False, "Neutral feedback"),
        ("This is terrible and I want a refund", False, "Direct negative, not sarcastic"),
        ("I love the new features, great work!", False, "Genuine praise"),
        
        # Borderline/ambiguous
        ("Well, that was interesting...", True, "Subtle sarcasm with ellipsis"),
        ("Perfect timing, just perfect", True, "Repeated 'perfect' often sarcastic"),
    ]
    
    for text, expected, description in test_cases:
        result = detector.detect(text)
        status = "✓" if result.is_sarcastic == expected else "✗"
        
        print(f"\n{status} {description}")
        print(f"   Text: \"{text}\"")
        print(f"   Sarcastic: {result.is_sarcastic} | Confidence: {result.confidence:.2%}")
        if result.indicators:
            print(f"   Indicators: {', '.join(result.indicators[:2])}")
        print(f"   Explanation: {result.explanation}")


def test_integrated_system():
    """Test sarcasm detection integrated with sentiment/emotion models."""
    print("\n" + "="*80)
    print("TESTING INTEGRATED SYSTEM (MODEL + SARCASM)")
    print("="*80)
    
    # Load model
    MODEL_DIR = ROOT_DIR / "models" / "saved_model"
    try:
        model = SentimentEmotionModel.load(MODEL_DIR)
    except FileNotFoundError:
        print("⚠️ No trained model found. Run training first: python src/train.py")
        return
    
    ensure_nltk_resources()
    
    # Test cases with sarcasm
    test_texts = [
        "Great job! You've managed to mess up my order three times in a row.",
        "Oh wonderful, another 'update' that broke everything. Thanks a lot!",
        "I'm so grateful for your 'help' that made things worse",
        "Fantastic customer service - if you consider being ignored for 2 weeks as service!",
        "Really appreciate being charged twice. So helpful!",
        # Non-sarcastic for comparison
        "Thank you for the quick resolution! Very satisfied with the support.",
        "Terrible experience, slow support, very disappointed.",
    ]
    
    for text in test_texts:
        print(f"\n{'─'*80}")
        print(f"📝 Text: \"{text}\"")
        print(f"{'─'*80}")
        
        cleaned = preprocess_text(text)
        result = model.predict_with_details(cleaned)
        
        # Display results
        print(f"\n📊 PREDICTIONS:")
        print(f"   Sentiment: {result['sentiment'].upper()} ({result['sentiment_confidence']:.1%})")
        print(f"   Emotion: {result['emotion'].upper()} ({result['emotion_confidence']:.1%})")
        
        if result.get('sarcasm_detected', False):
            print(f"\n🎭 SARCASM DETECTED:")
            print(f"   Confidence: {result['sarcasm_confidence']:.1%}")
            print(f"   Indicators: {', '.join(result['sarcasm_indicators'][:3])}")
        else:
            print(f"\n✅ No sarcasm detected")
        
        print(f"\n💡 EXPLANATION:")
        print(f"   {result['explanation']}")
        
        print(f"\n🎯 BUSINESS INSIGHT:")
        insight = result['business_insight']
        print(f"   Priority: {insight['priority']} | Category: {insight['category']}")
        print(f"   Action: {insight['action']}")


def main():
    """Run all tests."""
    print("\n" + "🧪 " + "="*76)
    print("SARCASM DETECTION TESTING SUITE")
    print("="*80)
    
    # Test standalone detector
    test_sarcasm_detector()
    
    # Test integrated system
    test_integrated_system()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
