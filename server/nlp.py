import re
import hashlib
from typing import Tuple, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

# Basic normalizer
def normalize_text(s: str) -> str:
    s = s.lower().strip()
    # remove urls/emails
    s = re.sub(r"https?://\S+|www\.\S+", " ", s)
    s = re.sub(r"\S+@\S+\.\S+", " ", s)
    # collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def sentiment_compound(s: str) -> float:
    return float(_analyzer.polarity_scores(s)["compound"])  # -1..1

def _has_any(s: str, kws: List[str]) -> bool:
    return any(k in s for k in kws)

def _clamp01(x: float) -> float:
    if x < 0: return 0.0
    if x > 1: return 1.0
    return float(x)

def score_urgency(text_norm: str, compound: float) -> float:
    # Heuristic: negative tone + urgent words + punctuation/caps
    urgent_kws = [
        "crash","urgent","asap","now","immediately","not working","down",
        "can't","cannot","error","fail","bug","broken","refund","cancel",
        "deadline","outage","blocker","stuck","hang","freeze"
    ]
    exclaim = text_norm.count("!")
    caps_ratio = 0.0  # we normalized to lowercase; keep 0 for now
    kw = 1.0 if _has_any(text_norm, urgent_kws) else 0.0
    # compound: -1 (very negative) .. +1 (very positive)
    # map negativity to urgency
    neg = max(0.0, -compound)  # 0..1
    raw = 0.55*neg + 0.35*kw + 0.10*min(exclaim/3.0, 1.0) + 0.0*caps_ratio
    return _clamp01(raw)

def score_impact(text_norm: str) -> float:
    # Heuristic: revenue/checkout/team-wide terms -> higher impact
    impact_kws = [
        "payment","checkout","billing","invoice","subscription","paying",
        "enterprise","admin","team","org","organization","workspace",
        "production","prod","release","customers","everyone","all users",
        "revenue","sales","trial conversion","onboarding","retention"
    ]
    longish = 1.0 if len(text_norm) >= 140 else 0.0  # longer = more context = maybe broader impact
    kw = 1.0 if _has_any(text_norm, impact_kws) else 0.0
    raw = 0.6*kw + 0.4*longish
    return _clamp01(raw)

def score_priority(urgency: float, impact: float) -> float:
    return _clamp01(0.6*urgency + 0.4*impact)

def simple_tags(text_norm: str, compound: float) -> list[str]:
    tags = []
    if compound <= -0.5: tags.append("very_negative")
    elif compound < 0: tags.append("negative")
    elif compound > 0.5: tags.append("very_positive")
    else: tags.append("neutral")
    if "feature request" in text_norm or "would be great" in text_norm:
        tags.append("feature_request")
    if "bug" in text_norm or "error" in text_norm or "not working" in text_norm:
        tags.append("bug")
    if "pricing" in text_norm or "billing" in text_norm or "payment" in text_norm:
        tags.append("billing")
    return tags
