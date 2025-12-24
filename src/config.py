"""Configuration for emotion taxonomy and business insights."""
from typing import Dict, List, Tuple

# ========================================
# EMOTION TAXONOMY (18 classes)
# ========================================

EMOTION_GROUPS = {
    "positive": [
        "joy",
        "satisfaction",
        "trust",
        "excitement",
        "gratitude",
        "relief",
    ],
    "negative": [
        "anger",
        "frustration",
        "disappointment",
        "sadness",
        "fear",
        "anxiety",
        "confusion",
        "annoyance",
        "regret",
    ],
    "neutral_cognitive": [
        "neutral",
        "curiosity",
        "surprise",
    ],
}

ALL_EMOTIONS = (
    EMOTION_GROUPS["positive"]
    + EMOTION_GROUPS["negative"]
    + EMOTION_GROUPS["neutral_cognitive"]
)

# ========================================
# SENTIMENT LABELS (3 classes)
# ========================================

SENTIMENTS = ["positive", "negative", "neutral"]

# ========================================
# INTENSITY THRESHOLDS
# ========================================

INTENSITY_THRESHOLDS = {
    "low": (0.0, 0.55),
    "medium": (0.55, 0.75),
    "high": (0.75, 1.0),
}

# ========================================
# MIXED EMOTION THRESHOLD
# ========================================

MIXED_EMOTION_THRESHOLD = 0.15  # If top-2 emotions differ by less than this, flag as mixed

# ========================================
# SARCASM DETECTION THRESHOLDS
# ========================================

SARCASM_CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to flag as sarcastic
SARCASM_HIGH_CONFIDENCE = 0.7  # High confidence sarcasm threshold

# Emotions prioritized when sarcasm is detected
SARCASM_PRIORITY_EMOTIONS = [
    "anger",
    "frustration", 
    "annoyance",
    "disappointment",
]

# ========================================
# BUSINESS INSIGHT MAPPING
# ========================================

BUSINESS_INSIGHTS: Dict[str, Dict[str, str]] = {
    # Positive emotions
    "joy": {
        "action": "Leverage for testimonials and marketing",
        "priority": "Low",
        "category": "Loyalty Opportunity",
    },
    "satisfaction": {
        "action": "Request reviews and referrals",
        "priority": "Low",
        "category": "Loyalty Opportunity",
    },
    "trust": {
        "action": "Nurture long-term relationship",
        "priority": "Low",
        "category": "Loyalty Opportunity",
    },
    "excitement": {
        "action": "Capitalize on enthusiasm with upsell",
        "priority": "Medium",
        "category": "Growth Opportunity",
    },
    "gratitude": {
        "action": "Acknowledge and strengthen relationship",
        "priority": "Low",
        "category": "Loyalty Opportunity",
    },
    "relief": {
        "action": "Follow up to ensure sustained satisfaction",
        "priority": "Medium",
        "category": "Recovery Success",
    },
    # Negative emotions
    "anger": {
        "action": "Immediate escalation to senior support",
        "priority": "Critical",
        "category": "Crisis Management",
    },
    "frustration": {
        "action": "Rapid response with clear solution path",
        "priority": "High",
        "category": "Issue Resolution",
    },
    "disappointment": {
        "action": "Proactive outreach with compensation offer",
        "priority": "High",
        "category": "Retention Risk",
    },
    "sadness": {
        "action": "Empathetic communication and support",
        "priority": "High",
        "category": "Retention Risk",
    },
    "fear": {
        "action": "Provide reassurance and security guarantees",
        "priority": "High",
        "category": "Trust Building",
    },
    "anxiety": {
        "action": "Transparent communication and frequent updates",
        "priority": "Medium",
        "category": "Trust Building",
    },
    "confusion": {
        "action": "Simplify communication and provide guidance",
        "priority": "Medium",
        "category": "User Experience Fix",
    },
    "annoyance": {
        "action": "Quick resolution to prevent escalation",
        "priority": "Medium",
        "category": "Issue Resolution",
    },
    "regret": {
        "action": "Win-back campaign with special offer",
        "priority": "High",
        "category": "Retention Risk",
    },
    # Neutral/Cognitive emotions
    "neutral": {
        "action": "Standard follow-up and satisfaction check",
        "priority": "Low",
        "category": "Routine Engagement",
    },
    "curiosity": {
        "action": "Provide educational content and demos",
        "priority": "Low",
        "category": "Engagement Opportunity",
    },
    "surprise": {
        "action": "Monitor context to understand if positive or negative",
        "priority": "Medium",
        "category": "Context Dependent",
    },
}

# ========================================
# EMOTION KEYWORDS (for explanation generation)
# ========================================

EMOTION_KEYWORDS: Dict[str, List[str]] = {
    "joy": [
        "love", "happy", "great", "excellent", "wonderful", "amazing", "fantastic",
        "brilliant", "perfect", "delighted", "thrilled", "pleased", "enjoy"
    ],
    "satisfaction": [
        "satisfied", "content", "pleased", "fulfilled", "good", "quality",
        "meets expectations", "worth it", "solid", "reliable", "effective"
    ],
    "trust": [
        "trust", "reliable", "dependable", "confident", "secure", "safe",
        "consistent", "professional", "credible", "honest", "transparent"
    ],
    "excitement": [
        "excited", "thrilling", "can't wait", "pumped", "eager", "energized",
        "wow", "awesome", "incredible", "outstanding", "spectacular"
    ],
    "gratitude": [
        "thank", "grateful", "appreciate", "thankful", "thanks", "blessing",
        "fortunate", "indebted", "much obliged", "acknowledge"
    ],
    "relief": [
        "relief", "finally", "glad", "resolved", "fixed", "better now",
        "phew", "at last", "sorted out", "worked out"
    ],
    "anger": [
        "angry", "furious", "outraged", "livid", "mad", "pissed", "ridiculous",
        "unacceptable", "disgusting", "terrible", "worst", "horrible", "awful"
    ],
    "frustration": [
        "frustrated", "annoying", "irritating", "stuck", "waste of time",
        "pointless", "useless", "inefficient", "complicated", "difficult"
    ],
    "disappointment": [
        "disappointed", "let down", "expected more", "underwhelming", "not impressed",
        "subpar", "lackluster", "mediocre", "falls short", "unmet expectations"
    ],
    "sadness": [
        "sad", "unhappy", "depressed", "upset", "miserable", "dejected",
        "disheartened", "gloomy", "sorrowful", "down", "blue"
    ],
    "fear": [
        "scared", "afraid", "worried", "frightened", "terrified", "nervous",
        "intimidated", "threatened", "concerned", "wary", "risky", "dangerous"
    ],
    "anxiety": [
        "anxious", "stress", "nervous", "uneasy", "tense", "worried",
        "apprehensive", "uncertain", "insecure", "panicked", "overwhelmed"
    ],
    "confusion": [
        "confused", "unclear", "don't understand", "what", "how", "why",
        "puzzled", "baffled", "lost", "complicated", "ambiguous", "vague"
    ],
    "annoyance": [
        "annoyed", "irritated", "bothersome", "nuisance", "petty", "minor issue",
        "slight problem", "mildly upset", "bit annoying", "somewhat irritating"
    ],
    "regret": [
        "regret", "wish I hadn't", "mistake", "should have", "if only",
        "remorse", "rue", "lament", "bad decision", "wrong choice"
    ],
    "neutral": [
        "okay", "fine", "average", "standard", "normal", "typical",
        "adequate", "acceptable", "moderate", "fair", "decent", "so-so"
    ],
    "curiosity": [
        "curious", "interested", "wondering", "intrigued", "want to know",
        "tell me more", "how does", "what is", "explore", "discover"
    ],
    "surprise": [
        "surprised", "unexpected", "shocked", "astonished", "amazed", "wow",
        "didn't expect", "unbelievable", "startling", "sudden", "out of nowhere"
    ],
}

# ========================================
# HELPER FUNCTIONS
# ========================================

def get_intensity(confidence: float) -> str:
    """Map confidence score to intensity level."""
    for level, (low, high) in INTENSITY_THRESHOLDS.items():
        if low <= confidence < high:
            return level
    return "high"


def get_business_insight(emotion: str) -> Dict[str, str]:
    """Get business insight for a given emotion."""
    return BUSINESS_INSIGHTS.get(emotion.lower(), {
        "action": "Monitor and follow standard procedures",
        "priority": "Low",
        "category": "Unknown",
    })


def get_emotion_group(emotion: str) -> str:
    """Get the group (positive/negative/neutral_cognitive) for an emotion."""
    emotion_lower = emotion.lower()
    for group, emotions in EMOTION_GROUPS.items():
        if emotion_lower in emotions:
            return group
    return "unknown"
