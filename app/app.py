"""Streamlit app for Intelligent Customer Emotion Analysis."""
from __future__ import annotations

from pathlib import Path
from typing import List
import sys

import pandas as pd
import streamlit as st

# Make local src modules importable when running from the app/ directory.
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from explainability import highlight_tokens
from model import SentimentEmotionModel
from preprocessing import ensure_nltk_resources, preprocess_text
from batch_analysis import BatchAnalyzer

st.set_page_config(
    page_title="Intelligent Customer Emotion Analysis", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL_DIR = Path(__file__).resolve().parent.parent / "models" / "saved_model"


@st.cache_resource(show_spinner=False)
def load_model() -> SentimentEmotionModel | None:
    try:
        return SentimentEmotionModel.load(MODEL_DIR)
    except FileNotFoundError:
        return None


def format_prediction(text: str, model: SentimentEmotionModel) -> dict:
    """Generate comprehensive prediction with all features."""
    cleaned = preprocess_text(text)
    
    # Use the enhanced prediction method
    result = model.predict_with_details(cleaned)
    
    # Add original text and cleaned text
    result["text"] = text
    result["clean_text"] = cleaned
    
    # Get token highlights for visualization
    result["sentiment_tokens"] = model.explain(cleaned, task="sentiment", top_n=6)
    result["emotion_tokens"] = model.explain(cleaned, task="emotion", top_n=6)
    
    return result


def analyze_file(file, model: SentimentEmotionModel) -> pd.DataFrame:
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file)
        if "text" not in df.columns:
            raise ValueError("CSV must have a 'text' column.")
        texts = df["text"].astype(str).tolist()
    elif file.name.lower().endswith(".txt"):
        texts = [line.decode("utf-8").strip() for line in file if line.strip()]
    else:
        raise ValueError("Unsupported file format. Use .txt or .csv")

    results = [format_prediction(text, model) for text in texts]
    return pd.DataFrame(results)


def main() -> None:
    # Header
    st.title("🧠 Intelligent Customer Emotion Analysis")
    st.markdown("**Multi-Dimensional NLP** | 18 Emotions | Business Insights | Explainable AI")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("📖 About")
        st.markdown("""
        This system analyzes customer feedback using:
        
        **🎯 Dual Classification**
        - 3 Sentiments (Pos/Neg/Neu)
        - 18 Fine-grained Emotions
        
        **✨ Key Features**
        - Confidence & Intensity Scoring
        - Mixed Emotion Detection
        - 🎭 Sarcasm Detection (NEW!)
        - Business Insight Mapping
        - Natural Language Explanations
        - Batch Analysis with Trends
        """)
        
        st.header("🎨 Emotion Groups")
        st.markdown("""
        **Positive**: Joy, Satisfaction, Trust, Excitement, Gratitude, Relief
        
        **Negative**: Anger, Frustration, Disappointment, Sadness, Fear, Anxiety, Confusion, Annoyance, Regret
        
        **Neutral/Cognitive**: Neutral, Curiosity, Surprise
        """)

    ensure_nltk_resources()
    model = load_model()

    if model is None:
        st.warning("⚠️ No trained model found. Run the training pipeline before using the app.")
        st.code("python src/train.py", language="bash")
        st.stop()

    tab_text, tab_file = st.tabs(["📝 Single Analysis", "📊 Batch Analysis"])

    with tab_text:
        st.subheader("Analyze Individual Feedback")
        user_text = st.text_area(
            "Enter customer feedback", 
            placeholder="Paste customer feedback, reviews, chat logs, or any text...",
            height=120
        )
        
        if st.button("🔍 Analyze", type="primary", use_container_width=True) and user_text.strip():
            with st.spinner("Analyzing emotions..."):
                result = format_prediction(user_text.strip(), model)
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Sentiment", 
                    result["sentiment"].upper(),
                    f"{result['sentiment_confidence']:.1%} confidence"
                )
                intensity_emoji = "🔥" if result["sentiment_intensity"] == "high" else "⚡" if result["sentiment_intensity"] == "medium" else "💡"
                st.caption(f"{intensity_emoji} {result['sentiment_intensity'].title()} Intensity")
            
            with col2:
                st.metric(
                    "Primary Emotion", 
                    result["emotion"].upper(),
                    f"{result['emotion_confidence']:.1%} confidence"
                )
                intensity_emoji = "🔥" if result["emotion_intensity"] == "high" else "⚡" if result["emotion_intensity"] == "medium" else "💡"
                st.caption(f"{intensity_emoji} {result['emotion_intensity'].title()} Intensity")
            
            with col3:
                if result["is_mixed_emotion"]:
                    st.metric(
                        "Secondary Emotion",
                        result["secondary_emotion"].upper(),
                        f"{result['secondary_confidence']:.1%} confidence"
                    )
                    st.caption("🎭 Mixed Emotion Detected")
                else:
                    st.metric("Emotion Type", "Single", "Clear signal")
                    st.caption("✅ No mixed emotions")
            
            with col4:
                insight = result["business_insight"]
                priority_emoji = "🚨" if insight["priority"] == "Critical" else "⚠️" if insight["priority"] == "High" else "📌"
                st.metric("Priority", insight["priority"], insight["category"])
                st.caption(f"{priority_emoji} {insight['category']}")
            
            # Sarcasm detection (if detected)
            if result.get("sarcasm_detected", False):
                st.warning(
                    f"🎭 **Sarcasm Detected** ({result['sarcasm_confidence']:.1%} confidence) - "
                    f"Ironic or sarcastic language may indicate underlying negativity despite positive surface words.",
                    icon="⚠️"
                )
            
            st.divider()
            
            # Explanation
            st.subheader("💡 AI Explanation")
            st.info(result["explanation"])
            
            # Business Insight
            st.subheader("🎯 Recommended Action")
            st.success(f"**{result['business_insight']['action']}**")
            
            st.divider()
            
            # Token highlights
            col_sent, col_emo = st.columns(2)
            
            with col_sent:
                st.markdown("**🎯 Sentiment Indicators**")
                st.markdown(
                    highlight_tokens(result["clean_text"], result["sentiment_tokens"]),
                    unsafe_allow_html=True,
                )
            
            with col_emo:
                st.markdown("**😊 Emotion Indicators**")
                st.markdown(
                    highlight_tokens(result["clean_text"], result["emotion_tokens"]),
                    unsafe_allow_html=True,
                )

    with tab_file:
        st.subheader("Batch Analysis with Emotion Trends")
        st.markdown("Upload a .txt or .csv file with multiple feedback entries to analyze trends.")
        
        uploaded = st.file_uploader(
            "Upload file", 
            type=["txt", "csv"], 
            accept_multiple_files=False,
            help="CSV files should have a 'text' column. TXT files should have one feedback per line."
        )
        
        if uploaded:
            try:
                with st.spinner("Processing batch..."):
                    df_results = analyze_file(uploaded, model)
                
                # Generate batch analysis
                predictions = df_results.to_dict('records')
                analyzer = BatchAnalyzer(predictions)
                summary = analyzer.generate_summary_report()
                
                # Display summary
                st.success(f"✅ Analyzed {summary['total_feedback']} feedback entries")
                
                # Trend summary
                st.markdown(analyzer.get_emotional_trend_text())
                
                st.divider()
                
                # Detailed metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**📊 Sentiment Distribution**")
                    for sent, pct in summary['sentiment_breakdown'].items():
                        st.progress(pct / 100, text=f"{sent.capitalize()}: {pct:.1f}%")
                
                with col2:
                    st.markdown("**😊 Top Emotions**")
                    for emotion, pct in summary['top_3_emotions'].items():
                        st.progress(pct / 100, text=f"{emotion.capitalize()}: {pct:.1f}%")
                
                with col3:
                    st.markdown("**⚠️ Priority Breakdown**")
                    for priority, count in summary['priority_breakdown'].items():
                        st.metric(priority, count)
                
                # Sarcasm metrics (if detected)
                if summary.get('sarcasm_rate', 0) > 0:
                    st.divider()
                    st.markdown("**🎭 Sarcasm Analysis**")
                    col_s1, col_s2 = st.columns(2)
                    
                    with col_s1:
                        st.metric(
                            "Sarcastic Feedback",
                            f"{summary['sarcasm_rate']:.1f}%",
                            "of total feedback"
                        )
                    
                    with col_s2:
                        # Show sarcastic feedback count
                        sarcastic_df = analyzer.sarcastic_feedback()
                        st.metric(
                            "High-Confidence Sarcasm",
                            len(sarcastic_df),
                            "items detected"
                        )
                
                st.divider()
                
                # High risk feedback
                high_risk = analyzer.high_risk_feedback()
                if len(high_risk) > 0:
                    st.subheader("🚨 High-Risk Feedback (Requires Immediate Attention)")
                    st.dataframe(high_risk, use_container_width=True)
                
                # Sarcastic feedback section
                sarcastic_df = analyzer.sarcastic_feedback()
                if len(sarcastic_df) > 0:
                    st.subheader("🎭 Sarcastic Feedback (Ironic Language Detected)")
                    st.markdown(
                        "These feedback entries contain sarcasm or ironic language. "
                        "Despite positive surface words, they may express underlying dissatisfaction."
                    )
                    st.dataframe(sarcastic_df, use_container_width=True)
                
                # Positive opportunities
                positive = analyzer.positive_opportunities()
                if len(positive) > 0:
                    st.subheader("✨ Positive Opportunities (Leverage for Growth)")
                    st.dataframe(positive, use_container_width=True)
                
                st.divider()
                
                # Full results
                with st.expander("📋 View All Predictions"):
                    display_cols = [
                        "text", "sentiment", "sentiment_confidence", "sentiment_intensity",
                        "emotion", "emotion_confidence", "emotion_intensity", "is_mixed_emotion"
                    ]
                    st.dataframe(df_results[display_cols], use_container_width=True)
                
                # Download
                st.download_button(
                    label="⬇️ Download Complete Results",
                    data=df_results.to_csv(index=False).encode("utf-8"),
                    file_name="emotion_analysis_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            except Exception as exc:
                st.error(f"❌ Could not process file: {exc}")
                st.exception(exc)


if __name__ == "__main__":
    main()
