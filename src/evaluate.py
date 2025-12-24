"""Evaluation utilities for trained models."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from .model import SentimentEmotionModel
from .preprocessing import preprocess_series

DEFAULT_TEST = Path("data/processed/test.csv")
DEFAULT_MODELS = Path("models/saved_model")
DEFAULT_OUTPUT = Path("data/processed")


def load_test_data(test_path: Path) -> pd.DataFrame:
    if not test_path.exists():
        raise FileNotFoundError(f"Test split not found at {test_path}")
    df = pd.read_csv(test_path)
    if "clean_text" not in df.columns:
        df["clean_text"] = preprocess_series(df["text"].fillna(""))
    # Filter out any rows with NaN in clean_text
    df = df[df["clean_text"].notna() & (df["clean_text"] != "")]
    return df


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Tuple[str, ...],
    title: str,
    out_path: Path,
) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(matrix, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(len(labels)), yticks=np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    ax.set_ylabel("True label")
    ax.set_xlabel("Predicted label")
    ax.set_title(title)

    thresh = matrix.max() / 2.0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(
                j,
                i,
                format(matrix[i, j], "d"),
                ha="center",
                va="center",
                color="white" if matrix[i, j] > thresh else "black",
            )

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def evaluate(model: SentimentEmotionModel, df: pd.DataFrame, output_dir: Path) -> dict:
    preds = model.predict(df["clean_text"])

    sentiment_report = classification_report(
        df["sentiment"], preds["sentiment"], output_dict=True, zero_division=0
    )
    emotion_report = classification_report(
        df["emotion"], preds["emotion"], output_dict=True, zero_division=0
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    plot_confusion_matrix(
        df["sentiment"].to_numpy(),
        preds["sentiment"],
        labels=tuple(sorted(df["sentiment"].unique())),
        title="Sentiment Confusion Matrix",
        out_path=output_dir / "sentiment_confusion.png",
    )
    plot_confusion_matrix(
        df["emotion"].to_numpy(),
        preds["emotion"],
        labels=tuple(sorted(df["emotion"].unique())),
        title="Emotion Confusion Matrix",
        out_path=output_dir / "emotion_confusion.png",
    )

    return {"sentiment": sentiment_report, "emotion": emotion_report}


def run(args: argparse.Namespace) -> None:
    test_path = Path(args.test)
    model_dir = Path(args.models_dir)
    output_dir = Path(args.output_dir)

    df_test = load_test_data(test_path)
    model = SentimentEmotionModel.load(model_dir)
    metrics = evaluate(model, df_test, output_dir)

    with (output_dir / "evaluation.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Evaluation complete. Reports saved to", output_dir)
    print(json.dumps(metrics, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate trained sentiment and emotion models")
    parser.add_argument("--test", type=str, default=str(DEFAULT_TEST), help="Path to test CSV")
    parser.add_argument("--models-dir", type=str, default=str(DEFAULT_MODELS), help="Directory with saved models")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help="Where to save reports and plots",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
