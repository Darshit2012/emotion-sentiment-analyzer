"""Batch and single-text prediction helper."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .model import SentimentEmotionModel
from .preprocessing import ensure_nltk_resources, preprocess_text

DEFAULT_MODELS = Path("models/saved_model")
DEFAULT_OUTPUT = Path("data/processed/predictions.csv")


def load_texts(file_path: Path | None, text: str | None) -> List[str]:
    if text:
        return [text]
    if file_path is None:
        raise ValueError("Provide either --text or --file for prediction.")
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
        if "text" not in df.columns:
            raise ValueError("CSV must have a 'text' column for predictions.")
        return df["text"].astype(str).tolist()
    if file_path.suffix.lower() == ".txt":
        return [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    raise ValueError("Unsupported file format. Use .txt or .csv")


def predict(
    texts: Iterable[str],
    model_dir: Path,
    output_path: Path,
) -> pd.DataFrame:
    model = SentimentEmotionModel.load(model_dir)
    ensure_nltk_resources()

    cleaned = [preprocess_text(t) for t in texts]
    preds = model.predict(cleaned)
    probs = model.predict_proba(cleaned)

    sentiment_classes = list(model.sentiment_model.named_steps["clf"].classes_)
    emotion_classes = list(model.emotion_model.named_steps["clf"].classes_)

    rows = []
    for idx, text in enumerate(texts):
        sentiment = preds["sentiment"][idx]
        emotion = preds["emotion"][idx]

        sentiment_prob = probs["sentiment"][idx]
        emotion_prob = probs["emotion"][idx]
        sentiment_conf = float(sentiment_prob[sentiment_classes.index(sentiment)])
        emotion_conf = float(emotion_prob[emotion_classes.index(emotion)])

        rows.append(
            {
                "text": text,
                "clean_text": cleaned[idx],
                "sentiment": sentiment,
                "sentiment_confidence": round(sentiment_conf, 4),
                "emotion": emotion,
                "emotion_confidence": round(emotion_conf, 4),
            }
        )

    df_out = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_path, index=False)
    return df_out


def run(args: argparse.Namespace) -> None:
    texts = load_texts(Path(args.file) if args.file else None, args.text)
    output_path = Path(args.output)
    df = predict(texts, Path(args.models_dir), output_path)
    print("Predictions saved to", output_path)
    print(df)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predict sentiment and emotion")
    parser.add_argument("--text", type=str, help="Single text to classify")
    parser.add_argument("--file", type=str, help="Path to .txt or .csv with text column")
    parser.add_argument("--models-dir", type=str, default=str(DEFAULT_MODELS), help="Directory containing saved models")
    parser.add_argument(
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help="Where to store the predictions CSV",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
