"""Text cleaning and preprocessing utilities for customer emotion analysis."""
import re
import string
from typing import Iterable, List

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Regex patterns for cleaning
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
HTML_PATTERN = re.compile(r"<.*?>")
EMOJI_PATTERN = re.compile(
    "["  # pylint: disable=raw-string-not-supported
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "]",
    flags=re.UNICODE,
)


def ensure_nltk_resources() -> None:
    """Download required NLTK resources if they are missing."""
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")


def strip_urls(text: str) -> str:
    return URL_PATTERN.sub("", text)


def strip_html(text: str) -> str:
    return HTML_PATTERN.sub(" ", text)


def strip_emojis(text: str) -> str:
    return EMOJI_PATTERN.sub("", text)


def strip_punctuation(text: str) -> str:
    return text.translate(str.maketrans("", "", string.punctuation))


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str) -> str:
    """Lowercase and remove noise such as URLs, HTML, emojis, and punctuation."""
    if not isinstance(text, str):
        return ""
    lowered = text.lower()
    lowered = strip_urls(lowered)
    lowered = strip_html(lowered)
    lowered = strip_emojis(lowered)
    lowered = strip_punctuation(lowered)
    lowered = normalize_whitespace(lowered)
    return lowered


def tokenize(text: str) -> List[str]:
    return word_tokenize(text)


def remove_stopwords(tokens: Iterable[str]) -> List[str]:
    stop_words = set(stopwords.words("english"))
    return [tok for tok in tokens if tok not in stop_words]


def preprocess_text(text: str) -> str:
    """Full preprocessing pipeline returning a cleaned string."""
    cleaned = clean_text(text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    return " ".join(tokens)


def preprocess_series(texts: Iterable[str]) -> List[str]:
    """Apply preprocessing to an iterable of texts."""
    ensure_nltk_resources()
    return [preprocess_text(t) for t in texts]
