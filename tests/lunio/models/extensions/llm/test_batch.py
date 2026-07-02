from lunio.models.extensions.llm.batch import _flatten_llm_result


def test_flatten_llm_result_prefixes_output_fields() -> None:
    flattened = _flatten_llm_result(
        {
            "decision": "review",
            "confidence": "medium",
            "risk_categories": ["click_quality", "unknown_content"],
            "rationale": "Needs review.",
            "missing_evidence": ["page_body"],
        }
    )

    assert flattened["llm_safety_decision"] == "review"
    assert flattened["llm_safety_confidence"] == "medium"
    assert flattened["llm_risk_categories"] == "click_quality;unknown_content"
    assert flattened["llm_missing_evidence"] == "page_body"
