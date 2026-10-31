import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lightweight sentiment lexicon with valence ratings
SENTIMENT_LEXICON = {
    # High Positive (+2 to +3)
    "excellent": 2.8, "outstanding": 3.0, "amazing": 2.8, "fantastic": 2.7,
    "incredible": 2.6, "love": 2.5, "perfect": 2.9, "superb": 2.7,
    "awesome": 2.5, "great": 2.0, "best": 2.5, "favorite": 2.2,
    # Mild Positive (+1 to +1.9)
    "good": 1.5, "nice": 1.3, "solid": 1.4, "pleased": 1.5, "happy": 1.6,
    "recommend": 1.8, "comfortable": 1.7, "durable": 1.6, "quality": 1.5,
    "smooth": 1.3, "fast": 1.2, "authentic": 1.6, "worth": 1.5,
    "aesthetic": 1.4, "responsive": 1.5, "clean": 1.2, "helpful": 1.4,
    # High Negative (-2 to -3)
    "terrible": -2.8, "horrible": -2.9, "worst": -3.0, "awful": -2.7,
    "scam": -3.0, "fake": -2.8, "waste": -2.5, "broken": -2.4,
    "damaged": -2.3, "useless": -2.6, "hate": -2.5, "disaster": -2.7,
    # Mild Negative (-1 to -1.9)
    "bad": -1.5, "poor": -1.6, "cheap": -1.3, "slow": -1.2, "delayed": -1.3,
    "disappointed": -1.8, "defective": -1.7, "flimsy": -1.5, "uncomfortable": -1.6,
    "rough": -1.2, "issue": -1.1, "problem": -1.3, "expensive": -1.1, "overpriced": -1.5
}

BOOSTERS = {
    "very": 1.4, "extremely": 1.6, "super": 1.5, "incredibly": 1.6,
    "really": 1.3, "so": 1.2, "totally": 1.3, "absolutely": 1.5
}

NEGATIONS = {"not", "never", "no", "hardly", "barely", "scarcely", "isnt", "wasnt", "arent", "dont", "doesnt", "didnt"}

class SentimentAnalyzer:
    def analyze_text(self, text: str) -> dict:
        """
        Analyzes a single review comment.
        Returns:
            {
                "polarity": float (-1.0 to 1.0),
                "label": "positive" | "neutral" | "negative",
                "confidence": float (0.0 to 1.0),
                "key_indicators": list[str],
                "is_estimate": True
            }
        """
        if not text or not text.strip():
            return {
                "polarity": 0.0,
                "label": "neutral",
                "confidence": 0.5,
                "key_indicators": [],
                "is_estimate": True
            }

        # Tokenize and clean
        words = re.findall(r"\b[\w'-]+\b", text.lower())
        total_score = 0.0
        matches = 0
        key_indicators = []

        is_negated = False
        booster_multiplier = 1.0

        for i, word in enumerate(words):
            if word in NEGATIONS:
                is_negated = True
                continue

            if word in BOOSTERS:
                booster_multiplier = BOOSTERS[word]
                continue

            if word in SENTIMENT_LEXICON:
                score = SENTIMENT_LEXICON[word] * booster_multiplier
                if is_negated:
                    score = -score * 0.8
                    indicator = f"not {word}"
                else:
                    indicator = word

                total_score += score
                matches += 1
                key_indicators.append(indicator)

                # Reset modifiers after scoring a valence word
                is_negated = False
                booster_multiplier = 1.0

        if matches > 0:
            avg_score = total_score / matches
            # Normalize to [-1.0, 1.0]
            normalized = max(-1.0, min(1.0, avg_score / 2.5))
        else:
            normalized = 0.0

        polarity = round(normalized, 3)
        if polarity > 0.15:
            label = "positive"
        elif polarity < -0.15:
            label = "negative"
        else:
            label = "neutral"

        confidence = round(min(0.95, 0.5 + (abs(polarity) * 0.45)), 2)

        return {
            "polarity": polarity,
            "label": label,
            "confidence": confidence,
            "key_indicators": key_indicators[:5],
            "is_estimate": True
        }

    def aggregate_reviews(self, reviews: list[dict]) -> dict:
        """
        Aggregates multiple review scores for a product.
        """
        if not reviews:
            return {
                "total_reviews": 0,
                "average_sentiment": 0.0,
                "positive_pct": 0.0,
                "neutral_pct": 0.0,
                "negative_pct": 0.0,
                "summary": "No customer reviews yet.",
                "is_estimate": True
            }

        pos_count = 0
        neu_count = 0
        neg_count = 0
        total_polarity = 0.0

        for r in reviews:
            score = r.get("sentiment_score", 0.0)
            total_polarity += score
            label = r.get("sentiment_label", "neutral")
            if label == "positive":
                pos_count += 1
            elif label == "negative":
                neg_count += 1
            else:
                neu_count += 1

        n = len(reviews)
        avg_polarity = round(total_polarity / n, 2)
        pos_pct = round((pos_count / n) * 100, 1)
        neu_pct = round((neu_count / n) * 100, 1)
        neg_pct = round((neg_count / n) * 100, 1)

        if pos_pct >= 65:
            summary = f"Overwhelmingly positive sentiment ({pos_pct}% positive feedback)."
        elif neg_pct >= 40:
            summary = f"Mixed/cautionary reception ({neg_pct}% critical comments)."
        else:
            summary = "Balanced feedback across customer community."

        return {
            "total_reviews": n,
            "average_sentiment": avg_polarity,
            "positive_pct": pos_pct,
            "neutral_pct": neu_pct,
            "negative_pct": neg_pct,
            "summary": summary,
            "is_estimate": True
        }

sentiment_analyzer = SentimentAnalyzer()
