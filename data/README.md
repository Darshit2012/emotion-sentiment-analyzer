# Data Directory

This directory contains the training and evaluation datasets.

## Structure

```
data/
├── raw/
│   ├── expanded_feedback.csv    # Main training dataset (21,045 samples)
│   └── sample_feedback.csv      # Small sample dataset
└── processed/
    ├── train.csv               # Training split (70%)
    ├── val.csv                 # Validation split (10%)  
    ├── test.csv                # Test split (20%)
    └── metrics.json            # Model evaluation metrics
```

## Dataset Information

**Training Dataset**: 21,045 customer feedback samples
- **Sentiments**: 3 classes (Positive, Negative, Neutral)
- **Emotions**: 18 fine-grained classes
- **Balance**: All emotion classes have 900+ samples

### Emotion Classes (18)

**Positive (6)**: joy, satisfaction, trust, excitement, gratitude, relief
**Negative (9)**: anger, frustration, disappointment, sadness, fear, anxiety, confusion, annoyance, regret
**Neutral (3)**: neutral, curiosity, surprise

## Data Privacy

⚠️ **Note**: The processed splits (train/val/test) and evaluation outputs are generated files and should not be committed to Git. Only the raw training data is tracked.

## Regenerating Data

If you need to regenerate the processed splits:

```bash
python src/train.py
```

This will automatically create train/val/test splits and save them to `data/processed/`.
