"""Rule-based advertiser-specific placement safety scoring."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from urllib.parse import unquote, urlparse

import pandas as pd

from lunio.models.rules_based.policies import (
    UNIVERSAL_REVIEW_CATEGORIES,
    UNIVERSAL_UNSAFE_CATEGORIES,
    get_policy,
)


class Decision(StrEnum):
    """Placement safety decision."""

    SAFE = "safe"
    REVIEW = "review"
    UNSAFE = "unsafe"


class Confidence(StrEnum):
    """Coarse decision confidence."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class PlacementScore:
    """Scored placement output."""

    decision: Decision
    confidence: Confidence
    risk_categories: tuple[str, ...]
    matched_signals: tuple[str, ...]
    rationale: str


CATEGORY_KEYWORDS = {
    "tobacco_or_nicotine": (
        "tobacco",
        "smoking",
        "smoke",
        "nicotine",
        "vaping",
        "vape",
        "quit smoking",
        "no tobacco",
    ),
    "aviation_incident": (
        "flight disaster",
        "flight disasters",
        "plane crash",
        "air crash",
        "crash",
        "near miss",
        "near-miss",
        "aviation safety",
        "investigation",
        "accident",
    ),
    "war_or_conflict": (
        "war",
        "conflict",
        "ukraine",
        "geopolitics",
        "terrorism",
        "terror",
    ),
    "weapons": (
        "weapon",
        "weapons",
        "gun",
        "guns",
        "firearm",
        "firearms",
    ),
    "politics": (
        "politics",
        "policy",
        "election",
        "maga",
        "rally",
        "government",
        "newsletters",
    ),
    "immigration": (
        "immigration",
        "asylum",
        "migrant",
        "migrants",
        "refugee",
        "border",
    ),
    "extremism": (
        "extremism",
        "extremist",
        "radicalisation",
        "radicalization",
    ),
    "hate_or_alt_right": (
        "alt-right",
        "alt right",
        "hate",
        "propaganda",
    ),
    "propaganda_or_disinformation": (
        "propaganda",
        "disinformation",
        "misinformation",
    ),
    "mental_health": (
        "mental health",
        "wellbeing",
        "depression",
        "anxiety",
        "self-harm",
    ),
    "adult_or_relationships": (
        "sex education",
        "sex & relationships",
        "relationships education",
        "sexual",
    ),
    "explicit_sexual_content": (
        "porn",
        "explicit sex",
        "explicit sexual",
    ),
}

HIGH_CONFIDENCE_SOURCES = {"topic", "title"}
INVALID_CLICK_RATE_THRESHOLD = 0.08


def score_dataframe(dataframe: pd.DataFrame, use_enriched_fields: bool) -> pd.DataFrame:
    """Score a placement dataframe and append safety columns."""

    scores = [
        score_placement(row.to_dict(), use_enriched_fields=use_enriched_fields)
        for _, row in dataframe.iterrows()
    ]

    scored = dataframe.copy()
    scored["safety_decision"] = [score.decision.value for score in scores]
    scored["safety_confidence"] = [score.confidence.value for score in scores]
    scored["risk_categories"] = [";".join(score.risk_categories) for score in scores]
    scored["matched_signals"] = [";".join(score.matched_signals) for score in scores]
    scored["safety_rationale"] = [score.rationale for score in scores]
    return scored


def score_placement(
    placement: dict[str, Any], *, use_enriched_fields: bool = True
) -> PlacementScore:
    """Score one placement for advertiser-specific safety."""

    company_name = str(placement["company_name"])
    policy = get_policy(company_name)

    signals = _build_text_signals(placement, use_enriched_fields=use_enriched_fields)
    risk_categories, matched_signals = _detect_risk_categories(signals)

    click_quality = _click_quality_risk(placement)
    if click_quality is not None:
        risk_categories.add("click_quality")
        matched_signals.append(click_quality)

    unknown_content = not any(
        source in HIGH_CONFIDENCE_SOURCES for source, _ in signals
    )
    if unknown_content and not risk_categories:
        risk_categories.add("unknown_content")
        matched_signals.append("raw-url-only:no usable title/topic signal")

    decision = _decision_for_categories(risk_categories, policy)
    confidence = _confidence_for_decision(
        decision=decision,
        risk_categories=risk_categories,
        matched_signals=matched_signals,
        use_enriched_fields=use_enriched_fields,
    )
    rationale = _build_rationale(
        company_name=company_name,
        decision=decision,
        risk_categories=risk_categories,
        matched_signals=matched_signals,
        use_enriched_fields=use_enriched_fields,
    )

    return PlacementScore(
        decision=decision,
        confidence=confidence,
        risk_categories=tuple(sorted(risk_categories)),
        matched_signals=tuple(matched_signals),
        rationale=rationale,
    )


def _build_text_signals(
    placement: dict[str, Any], *, use_enriched_fields: bool
) -> list[tuple[str, str]]:
    """Collect topic, title, and URL text used for keyword risk matching."""

    signals = []

    if use_enriched_fields:
        for field in ("topic", "title"):
            value = placement.get(field)
            if pd.notna(value) and str(value).strip():
                signals.append((field, str(value)))

    url = str(placement.get("url", ""))
    parsed_url = urlparse(url)
    url_text = " ".join(
        [
            parsed_url.netloc,
            unquote(parsed_url.path).replace("/", " ").replace("-", " "),
            unquote(parsed_url.query).replace("&", " ").replace("=", " "),
        ]
    )
    signals.append(("url", url_text))

    return signals


def _detect_risk_categories(
    signals: list[tuple[str, str]],
) -> tuple[set[str], list[str]]:
    risk_categories = set()
    matched_signals = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        for source, text in signals:
            normalized_text = text.lower()
            matched_keyword = next(
                (keyword for keyword in keywords if keyword in normalized_text),
                None,
            )
            if matched_keyword:
                risk_categories.add(category)
                matched_signals.append(f"{source}:{matched_keyword}->{category}")
                break

    return risk_categories, matched_signals


def _click_quality_risk(placement: dict[str, Any]) -> str | None:
    """Return a click-quality signal when invalid-click rate is unusually high."""

    clicks = placement.get("clicks")
    invalid_clicks = placement.get("invalid_clicks")
    if pd.isna(clicks) or pd.isna(invalid_clicks):
        return None

    clicks = float(clicks)
    invalid_clicks = float(invalid_clicks)
    if clicks <= 0:
        return None

    invalid_rate = invalid_clicks / clicks
    if invalid_rate >= INVALID_CLICK_RATE_THRESHOLD:
        return f"invalid_click_rate:{invalid_rate:.1%}->click_quality"
    return None


def _decision_for_categories(risk_categories: set[str], policy: Any) -> Decision:
    """Map detected risk categories to the strongest applicable safety decision."""

    # Any overlap with universal or advertiser-specific unsafe categories wins.
    if risk_categories & (UNIVERSAL_UNSAFE_CATEGORIES | policy.unsafe_categories):
        return Decision.UNSAFE
    if risk_categories & (UNIVERSAL_REVIEW_CATEGORIES | policy.review_categories):
        return Decision.REVIEW
    return Decision.SAFE


def _confidence_for_decision(
    *,
    decision: Decision,
    risk_categories: set[str],
    matched_signals: list[str],
    use_enriched_fields: bool,
) -> Confidence:
    """Estimate confidence from evidence quality and matched risk signals."""

    has_enriched_signal = any(
        signal.split(":", 1)[0] in HIGH_CONFIDENCE_SOURCES for signal in matched_signals
    )
    if decision == Decision.SAFE and not use_enriched_fields:
        return Confidence.LOW
    if "unknown_content" in risk_categories:
        return Confidence.LOW
    if has_enriched_signal:
        return Confidence.HIGH
    if matched_signals:
        return Confidence.MEDIUM
    return Confidence.LOW


def _build_rationale(
    *,
    company_name: str,
    decision: Decision,
    risk_categories: set[str],
    matched_signals: list[str],
    use_enriched_fields: bool,
) -> str:
    """Build a human-readable explanation for the placement score."""

    mode = "enriched title/topic" if use_enriched_fields else "raw URL"
    if not risk_categories:
        return (
            f"{decision.value.title()} for {company_name}: no configured high-risk "
            f"signals were detected from {mode} evidence."
        )

    categories = ", ".join(sorted(risk_categories))
    signals = "; ".join(matched_signals)
    return (
        f"{decision.value.title()} for {company_name}: detected {categories} "
        f"from {mode} evidence. Signals: {signals}."
    )
