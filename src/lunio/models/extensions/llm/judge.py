"""Prompt assets for an optional LLM placement safety judge."""

from typing import Any

from lunio.models.policies import get_policy

SAFETY_JUDGE_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "decision": {"type": "string", "enum": ["safe", "review", "unsafe"]},
        "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
        "risk_categories": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
        "missing_evidence": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "decision",
        "confidence",
        "risk_categories",
        "rationale",
        "missing_evidence",
    ],
}


def build_llm_judge_prompt(placement: dict[str, Any]) -> str:
    """Build a constrained prompt for an LLM safety judge."""

    company_name = str(placement["company_name"])

    # Get the advertiser's policy to include in the prompt
    policy = get_policy(company_name)

    return f"""You are judging advertiser-specific ad placement safety.

Advertiser:
- name: {policy.company_name}
- policy: {policy.description}
- hard unsafe categories: {", ".join(sorted(policy.unsafe_categories))}
- review categories: {", ".join(sorted(policy.review_categories))}

Placement evidence:
- url: {placement.get("url", "")}
- title: {placement.get("title", "")}
- topic: {placement.get("topic", "")}
- channel_type: {placement.get("channel_type", "")}
- clicks: {placement.get("clicks", "")}
- invalid_clicks: {placement.get("invalid_clicks", "")}

Instructions:
- Decide whether this placement is safe, review, or unsafe for this advertiser.
- Treat missing title/topic/body evidence as uncertainty, not safety.
- Do not infer facts that are not supported by the supplied evidence.
- Prefer review when evidence is weak or the page may be sensitive.
- Return only JSON matching this schema:
{SAFETY_JUDGE_JSON_SCHEMA}
"""
