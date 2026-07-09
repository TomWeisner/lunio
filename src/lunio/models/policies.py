"""Advertiser-specific placement safety policies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AdvertiserPolicy:
    """Risk policy for a single advertiser."""

    company_name: str
    description: str
    unsafe_categories: frozenset[str]
    review_categories: frozenset[str]


UNIVERSAL_UNSAFE_CATEGORIES = frozenset(
    {
        "extremism",
        "hate_or_alt_right",
        "weapons",
        "explicit_sexual_content",
        "propaganda_or_disinformation",
    }
)

UNIVERSAL_REVIEW_CATEGORIES = frozenset(
    {
        "politics",
        "immigration",
        "war_or_conflict",
        "mental_health",
        "tobacco_or_nicotine",
        "aviation_incident",
        "adult_or_relationships",
        "click_quality",
        "unknown_content",
    }
)

ADVERTISER_POLICIES = {
    "Jet3 Holidays": AdvertiserPolicy(
        company_name="Jet3 Holidays",
        description=(
            "Travel advertiser. Extra-sensitive to aviation incidents, "
            "transport disruption, war, terrorism, and travel-adjacent disasters."
        ),
        unsafe_categories=frozenset(
            {
                "aviation_incident",
                "war_or_conflict",
                "extremism",
                "hate_or_alt_right",
                "weapons",
                "propaganda_or_disinformation",
            }
        ),
        review_categories=frozenset(
            {
                "politics",
                "immigration",
                "tobacco_or_nicotine",
                "mental_health",
                "click_quality",
                "unknown_content",
            }
        ),
    ),
    "Jen & Berry's Ice Cream": AdvertiserPolicy(
        company_name="Jen & Berry's Ice Cream",
        description=(
            "Family-friendly food brand. Sensitive to tobacco/nicotine, adult "
            "themes, extremism, weapons, and divisive political content."
        ),
        unsafe_categories=frozenset(
            {
                "tobacco_or_nicotine",
                "explicit_sexual_content",
                "extremism",
                "hate_or_alt_right",
                "weapons",
            }
        ),
        review_categories=frozenset(
            {
                "adult_or_relationships",
                "politics",
                "immigration",
                "war_or_conflict",
                "mental_health",
                "propaganda_or_disinformation",
                "click_quality",
                "unknown_content",
            }
        ),
    ),
    "Moonbucks Coffee": AdvertiserPolicy(
        company_name="Moonbucks Coffee",
        description=(
            "Broad-reach coffee brand. Blocks universal high-risk content but "
            "can tolerate more neutral news and general-interest content."
        ),
        unsafe_categories=frozenset(
            {
                "extremism",
                "hate_or_alt_right",
                "weapons",
                "explicit_sexual_content",
                "propaganda_or_disinformation",
            }
        ),
        review_categories=frozenset(
            {
                "politics",
                "immigration",
                "war_or_conflict",
                "tobacco_or_nicotine",
                "aviation_incident",
                "mental_health",
                "click_quality",
                "unknown_content",
            }
        ),
    ),
    "Plush Cosmetics": AdvertiserPolicy(
        company_name="Plush Cosmetics",
        description=(
            "Beauty and cosmetics advertiser. Sensitive to harmful wellbeing, "
            "controversial political, extremist, tobacco, sexual, and violent content."
        ),
        unsafe_categories=frozenset(
            {
                "extremism",
                "hate_or_alt_right",
                "weapons",
                "explicit_sexual_content",
                "propaganda_or_disinformation",
                "tobacco_or_nicotine",
            }
        ),
        review_categories=frozenset(
            {
                "politics",
                "immigration",
                "war_or_conflict",
                "mental_health",
                "adult_or_relationships",
                "aviation_incident",
                "click_quality",
                "unknown_content",
            }
        ),
    ),
}


def get_policy(company_name: str) -> AdvertiserPolicy:
    """Return the policy for an advertiser."""

    try:
        return ADVERTISER_POLICIES[company_name]
    except KeyError as error:
        known_advertisers = ", ".join(sorted(ADVERTISER_POLICIES))
        msg = (
            f"Unknown advertiser {company_name!r}. "
            f"Known advertisers: {known_advertisers}"
        )
        raise ValueError(msg) from error
