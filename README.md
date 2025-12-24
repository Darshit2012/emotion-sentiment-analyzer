# 🧠 Intelligent Customer Emotion Analysis

> A multi-dimensional NLP system that analyzes customer feedback using 18 fine-grained emotions, sentiment classification, and sarcasm detection.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=Streamlit&logoColor=white)](https://streamlit.io)

---

## 📌 Overview

Traditional sentiment analysis only classifies text as positive, negative, or neutral—but customer emotions are far more nuanced. This system goes beyond basic sentiment to identify **18 distinct emotions** like anger, frustration, gratitude, and confusion, enabling businesses to:

- **Prioritize urgent issues** (anger/frustration require immediate attention)
- **Identify retention risks** (disappointment, regret, sadness)
- **Leverage positive feedback** (gratitude, satisfaction for testimonials)
- **Detect sarcasm** (ironic language that traditional models misclassify)

Built as a **final-year B.Tech project**, this system combines explainable AI, business intelligence, and practical deployment through an interactive Streamlit web interface.

---

## ✨ Key Features

### 🎯 **18-Emotion Classification**
Identifies fine-grained emotions across three categories:
- **Positive** (6): Joy, Satisfaction, Trust, Excitement, Gratitude, Relief
- **Negative** (9): Anger, Frustration, Disappointment, Sadness, Fear, Anxiety, Confusion, Annoyance, Regret
- **Neutral/Cognitive** (3): Neutral, Curiosity, Surprise

### 🎭 **Sarcasm Detection**
- Rule-based detection of ironic language (e.g., "Great job breaking my order!")
- Prevents misclassification of sarcastic complaints as positive feedback
- 92% accuracy on explicit sarcasm patterns

### 📊 **Dual-Pipeline Architecture**
- Parallel TF-IDF + Logistic Regression models for sentiment and emotion
- 99.81% sentiment accuracy, 98.67% emotion accuracy
- Fast inference (~10ms per text)

### 💡 **Explainable AI**
- Highlights influential keywords for each prediction
- Natural language explanations (e.g., "Detected ANGER due to 'terrible', 'worst'")
- Transparency for business decision-making

### 🎯 **Business Insights**
Automatic recommendation mapping:
- **Critical Priority**: Anger → Immediate escalation
- **High Priority**: Frustration → Rapid response
- **Low Priority**: Satisfaction → Request reviews

### 📈 **Batch Analysis**
- Upload CSV/TXT files for trend analysis
- Emotion distribution, high-risk identification
- Downloadable reports with metrics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Darshit2012/emotion-sentiment-analyzer.git
   cd emotion-sentiment-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (first time only)
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

5. **Train the models**
   ```bash
   python src/train.py
   ```
   *This creates `models/saved_model/` with trained pipelines (~2-3 minutes)*

6. **Launch the web app**
   ```bash
   streamlit run app/app.py
   ```
   *Access at http://localhost:8501*

---

## 📂 Project Structure

```
emotion-sentiment-analyzer/
├── src/                      # Core source code
│   ├── model.py              # Dual-pipeline classifier
│   ├── sarcasm_detector.py   # Sarcasm detection module
│   ├── preprocessing.py      # Text cleaning
│   ├── train.py              # Training script
│   ├── evaluate.py           # Model evaluation
│   └── config.py             # Emotion taxonomy & settings
├── app/
│   └── app.py                # Streamlit web interface
├── data/
│   ├── raw/                  # Training datasets
│   └── processed/            # Generated splits (train/val/test)
├── models/
│   └── saved_model/          # Trained model artifacts (.joblib)
├── notebooks/
│   └── exploration.ipynb     # EDA and experiments
├── docs/                     # Detailed documentation
│   ├── SARCASM_FEATURE_SUMMARY.md
│   ├── PROJECT_UPGRADE_SUMMARY.md
│   └── ACCURACY_IMPROVEMENT_REPORT.md
├── tests/
│   ├── test_system.py        # System integration tests
│   └── test_sarcasm.py       # Sarcasm detection tests
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
└── README.md                 # This file
```

---

## 💻 Usage

### Single Text Analysis

```python
from pathlib import Path
from src.model import SentimentEmotionModel
from src.preprocessing import preprocess_text

# Load trained model
model = SentimentEmotionModel.load(Path("models/saved_model"))

# Analyze text
text = "Great job! You managed to break my order again."
cleaned = preprocess_text(text)
result = model.predict_with_details(cleaned)

print(f"Sentiment: {result['sentiment']} ({result['sentiment_confidence']:.1%})")
print(f"Emotion: {result['emotion']} ({result['emotion_confidence']:.1%})")
print(f"Sarcasm: {'Yes' if result['sarcasm_detected'] else 'No'}")
print(f"Explanation: {result['explanation']}")
```

**Output:**
```
Sentiment: NEUTRAL (52.2%)
Emotion: NEUTRAL (63.5%)
Sarcasm: Yes (75.0%)
Explanation: The model detected NEUTRAL with moderate confidence...
⚠️ Strong sarcasm detected (75.0%). Sarcasm signals: sarcastic phrase: 'great job'
```

### Streamlit Web Interface

The web app provides two modes:

1. **📝 Single Analysis**: Analyze individual feedback with detailed breakdowns
2. **📊 Batch Analysis**: Upload CSV/TXT files for trend analysis and reports

**Features:**
- Real-time emotion detection
- Sarcasm warning banners
- Token-level highlighting
- Business action recommendations
- Downloadable CSV reports

---

## 📊 Model Performance

### Accuracy Metrics
| Model | Accuracy | Dataset Size |
|-------|----------|-------------|
| Sentiment | 99.81% | 3,157 test samples |
| Emotion | 98.67% | 3,157 test samples |
| Sarcasm | 92.00% | 12 test cases |

### Per-Emotion F1-Scores
- **Perfect (1.000)**: Annoyance, Curiosity, Excitement, Gratitude, Sadness
- **Excellent (0.97+)**: Anger, Anxiety, Disappointment, Fear, Joy, Relief, Satisfaction, Trust
- **Good (0.93+)**: Confusion, Frustration

### Training Dataset
- **Total Samples**: 21,045
- **Sentiment Distribution**: Negative (52.3%), Positive (30.0%), Neutral (17.7%)
- **Emotion Balance**: All 18 classes have 900+ samples

---

## 🎓 Technical Details

### Architecture
- **Vectorization**: TF-IDF (max_features=12,000, ngram_range=(1,2))
- **Classification**: Logistic Regression (C=2.0, max_iter=3,000, balanced weights)
- **Sarcasm Detection**: Rule-based heuristics (5 detection strategies)

### Preprocessing Pipeline
1. Lowercase conversion
2. URL/HTML removal
3. Emoji handling
4. Stopword filtering
5. Lemmatization

### Sarcasm Detection Strategies
1. Known sarcastic phrases ("great job", "thanks a lot")
2. Positive words + negative context (contrast detection)
3. Quoted positive words ("great" service)
4. Excessive punctuation (!!!, ???)
5. Sentiment-emotion polarity mismatch

---

## 🧪 Testing

Run the test suites to verify system functionality:

```bash
# Test full system
python tests/test_system.py

# Test sarcasm detection
python tests/test_sarcasm.py
```

**Expected Results:**
- 18/18 emotion tests pass
- 11/12 sarcasm tests pass (92% accuracy)
- All integration tests pass

---

## 📈 Use Cases

### Customer Support
- **Triage tickets** by emotion urgency (anger/frustration = high priority)
- **Detect escalation risks** through negative emotion patterns
- **Identify training needs** from confusion/anxiety clusters

### Product Management
- **Feature feedback analysis**: Track satisfaction/excitement trends
- **Bug report prioritization**: Anger/frustration = critical issues
- **User research**: Understand emotional responses to features

### Marketing
- **Testimonial identification**: Gratitude/satisfaction for campaigns
- **Brand sentiment tracking**: Monitor emotion shifts over time
- **Crisis detection**: Spike in anger/disappointment = urgent response

---

## 🔧 Configuration

### Emotion Taxonomy
Modify `src/config.py` to customize:
- Emotion groups and labels
- Business insight mappings
- Priority levels
- Intensity thresholds

### Model Hyperparameters
Edit training settings in `src/train.py`:
```python
build_pipeline(max_features=12000, ngram_range=(1, 2))
LogisticRegression(C=2.0, max_iter=3000)
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

This is a final-year B.Tech project. While contributions are welcome, please note:
- Fork the repository and create feature branches
- Follow existing code style and documentation standards
- Add tests for new features
- Update README if adding significant functionality

---

## 📚 Documentation

- **Detailed Documentation**: See [docs/](docs/) folder
- **Sarcasm Feature**: [docs/SARCASM_FEATURE_SUMMARY.md](docs/SARCASM_FEATURE_SUMMARY.md)
- **Project Upgrades**: [docs/PROJECT_UPGRADE_SUMMARY.md](docs/PROJECT_UPGRADE_SUMMARY.md)
- **Accuracy Report**: [docs/ACCURACY_IMPROVEMENT_REPORT.md](docs/ACCURACY_IMPROVEMENT_REPORT.md)
- **Quick Start Guide**: [QUICK_START.md](QUICK_START.md)

---

## 👨‍💻 Author

**Darshit**
- Final-Year B.Tech Project (2025)
- GitHub: [@Darshit2012](https://github.com/Darshit2012)

---

## 🙏 Acknowledgments

- **scikit-learn** for ML infrastructure
- **NLTK** for NLP utilities
- **Streamlit** for web interface
- **Emotion Taxonomy** inspired by Plutchik's Wheel of Emotions

---

## 📊 Project Stats

- **Lines of Code**: ~3,500
- **Training Data**: 21,045 samples
- **Emotion Classes**: 18
- **Model Accuracy**: 98.67% (emotion)
- **Inference Speed**: ~10ms per text
- **Development Time**: Final-year project (2024-2025)

---

**⭐ If you find this project useful, please consider starring the repository!**

---

## 🔍 Quick Links

- [Installation](#installation)
- [Usage](#usage)
- [Model Performance](#model-performance)
- [Technical Details](#technical-details)
- [Testing](#testing)
- [License](#license)
