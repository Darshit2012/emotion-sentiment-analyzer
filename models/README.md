# Models Directory

This directory stores trained model artifacts.

## Structure

```
models/
└── saved_model/
    ├── sentiment_model.joblib    # Sentiment classification pipeline
    └── emotion_model.joblib      # Emotion classification pipeline
```

## Model Architecture

Both models use **TF-IDF + Logistic Regression** pipelines:

### Configuration
- **Vectorizer**: TF-IDF with max_features=12,000, ngram_range=(1,2)
- **Classifier**: Logistic Regression with C=2.0, max_iter=3,000
- **Class Weighting**: Balanced

### Performance
- **Sentiment Accuracy**: 99.81%
- **Emotion Accuracy**: 98.67%

## File Sizes

⚠️ **Note**: Model files (.joblib) are large (~50-100MB) and excluded from Git by default. You need to train the models locally.

## Training Models

To train the models from scratch:

```bash
python src/train.py
```

Models will be saved to `models/saved_model/` automatically.

## Loading Models

```python
from src.model import SentimentEmotionModel

model = SentimentEmotionModel.load(Path("models/saved_model"))
```
