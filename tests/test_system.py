"""Test script to demonstrate the upgraded emotion analysis system."""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from model import SentimentEmotionModel
from preprocessing import preprocess_text, ensure_nltk_resources

def test_single_prediction():
    """Test single prediction with all new features."""
    print("=" * 80)
    print("TESTING SINGLE PREDICTION WITH ENHANCED FEATURES")
    print("=" * 80)
    
    # Initialize
    ensure_nltk_resources()
    model = SentimentEmotionModel.load(Path("models/saved_model"))
    
    # Test cases
    test_cases = [
        "I am absolutely furious about the terrible service! This is unacceptable!",
        "Very satisfied with the product quality. It meets all my expectations.",
        "I'm a bit confused about how to use this feature. Need help.",
        "So grateful for the quick resolution! Thank you so much for the support!",
        "Scared that my data might be compromised. Is this secure?",
        "This is okay, nothing special. Average experience.",
        "Excited to try the new features! Can't wait to explore more!",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST CASE {i}: {text}")
        print(f"{'─' * 80}")
        
        cleaned = preprocess_text(text)
        result = model.predict_with_details(cleaned)
        
        # Display results
        print(f"\n📊 PREDICTIONS:")
        print(f"  Sentiment: {result['sentiment'].upper()} ({result['sentiment_confidence']:.1%}) - {result['sentiment_intensity'].upper()}")
        print(f"  Emotion: {result['emotion'].upper()} ({result['emotion_confidence']:.1%}) - {result['emotion_intensity'].upper()}")
        
        if result['is_mixed_emotion']:
            print(f"\n🎭 MIXED EMOTION DETECTED:")
            print(f"  Primary: {result['emotion'].upper()} ({result['emotion_confidence']:.1%})")
            print(f"  Secondary: {result['secondary_emotion'].upper()} ({result['secondary_confidence']:.1%})")
        
        print(f"\n💡 EXPLANATION:")
        print(f"  {result['explanation']}")
        
        insight = result['business_insight']
        print(f"\n🎯 BUSINESS INSIGHT:")
        print(f"  Priority: {insight['priority']} | Category: {insight['category']}")
        print(f"  Action: {insight['action']}")


def test_emotion_coverage():
    """Test all 18 emotions to verify model coverage."""
    print("\n\n" + "=" * 80)
    print("TESTING EMOTION COVERAGE (18 EMOTIONS)")
    print("=" * 80)
    
    ensure_nltk_resources()
    model = SentimentEmotionModel.load(Path("models/saved_model"))
    
    # Get all emotion classes from model
    emotion_classes = sorted(model.emotion_model.named_steps["clf"].classes_)
    
    print(f"\nTotal Emotions Supported: {len(emotion_classes)}")
    print(f"\nEmotion Classes:")
    for emotion in emotion_classes:
        print(f"  ✓ {emotion.capitalize()}")
    
    # Test sentiment classes
    sentiment_classes = sorted(model.sentiment_model.named_steps["clf"].classes_)
    print(f"\nTotal Sentiments Supported: {len(sentiment_classes)}")
    print(f"\nSentiment Classes:")
    for sentiment in sentiment_classes:
        print(f"  ✓ {sentiment.capitalize()}")


if __name__ == "__main__":
    test_emotion_coverage()
    test_single_prediction()
    
    print("\n\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
    print("\n🚀 Launch the Streamlit app to test the full UI:")
    print("   streamlit run app/app.py")
    print("\n🌐 Access the app at: http://localhost:8503")
    print("=" * 80)
