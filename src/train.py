"""Training pipeline for sentiment and emotion classifiers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from .preprocessing import ensure_nltk_resources, preprocess_series
from .model import SentimentEmotionModel


DEFAULT_DATA = Path("data/raw/expanded_feedback.csv")
DEFAULT_PROCESSED = Path("data/processed")
DEFAULT_MODELS = Path("models/saved_model")


def load_dataset(data_path: Path) -> pd.DataFrame:
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")
    df = pd.read_csv(data_path)
    expected_columns = {"text", "sentiment", "emotion"}
    if not expected_columns.issubset(df.columns):
        raise ValueError(
            f"Dataset must include columns {expected_columns}, found {set(df.columns)}"
        )
    return df


def preprocess_dataset(df: pd.DataFrame) -> pd.DataFrame:
    ensure_nltk_resources()
    df = df.copy()
    df["clean_text"] = preprocess_series(df["text"].fillna(""))
    return df


def split_data(
    df: pd.DataFrame, test_size: float, val_size: float, seed: int
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_train, df_test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=df["sentiment"]
    )
    df_train, df_val = train_test_split(
        df_train, test_size=val_size, random_state=seed, stratify=df_train["sentiment"]
    )
    return df_train, df_val, df_test


def train_models(df_train: pd.DataFrame) -> SentimentEmotionModel:
    model = SentimentEmotionModel()
    model.fit(
        texts=df_train["clean_text"],
        sentiment_labels=df_train["sentiment"],
        emotion_labels=df_train["emotion"],
    )
    return model


def evaluate_models(model: SentimentEmotionModel, df_split: pd.DataFrame) -> dict:
    predictions = model.predict(df_split["clean_text"])
    sentiment_report = classification_report(
        df_split["sentiment"],
        predictions["sentiment"],
        output_dict=True,
        zero_division=0,
    )
    emotion_report = classification_report(
        df_split["emotion"],
        predictions["emotion"],
        output_dict=True,
        zero_division=0,
    )
    return {"sentiment": sentiment_report, "emotion": emotion_report}


def save_artifacts(
    model: SentimentEmotionModel,
    metrics: dict,
    processed_dir: Path,
    models_dir: Path,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> None:
    processed_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    model.save(models_dir)
    (processed_dir / "train.csv").write_text(train_df.to_csv(index=False))
    (processed_dir / "val.csv").write_text(val_df.to_csv(index=False))
    (processed_dir / "test.csv").write_text(test_df.to_csv(index=False))
    with (processed_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def run(args: argparse.Namespace) -> None:
    data_path = Path(args.data)
    processed_dir = Path(args.processed_dir)
    models_dir = Path(args.models_dir)

    df = load_dataset(data_path)
    df = preprocess_dataset(df)
    df_train, df_val, df_test = split_data(
        df, test_size=args.test_size, val_size=args.val_size, seed=args.seed
    )

    # Option to include validation in training for maximum accuracy
    if args.use_val_for_training:
        print("INFO: Including validation data in training for maximum accuracy")
        df_train_combined = pd.concat([df_train, df_val], ignore_index=True)
        model = train_models(df_train_combined)
        print(f"   Training samples: {len(df_train_combined)} (train + val)")
    else:
        model = train_models(df_train)
        print(f"   Training samples: {len(df_train)}")
    
    metrics = {
        "validation": evaluate_models(model, df_val),
        "test": evaluate_models(model, df_test),
    }

    save_artifacts(model, metrics, processed_dir, models_dir, df_train, df_val, df_test)

    print("Training complete. Models saved to", models_dir)
    print("Validation:")
    print(json.dumps(metrics["validation"], indent=2))
    print("Test:")
    print(json.dumps(metrics["test"], indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train sentiment and emotion classifiers")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA), help="Path to CSV dataset")
    parser.add_argument(
        "--processed-dir",
        type=str,
        default=str(DEFAULT_PROCESSED),
        help="Directory to store processed data and metrics",
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default=str(DEFAULT_MODELS),
        help="Directory to store trained models",
    )
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split size")
    parser.add_argument(
        "--val-size",
        type=float,
        default=0.1,
        help="Validation split size applied on the training portion",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--use-val-for-training",
        action="store_true",
        help="Include validation data in training for maximum accuracy",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
