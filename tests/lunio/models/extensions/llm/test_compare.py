import pandas as pd

from lunio.models.extensions.llm.compare import compare_llm_with_rules


def test_compare_llm_with_rules_writes_comparison_and_summary(tmp_path) -> None:
    rules_path = tmp_path / "rules.csv"
    llm_path = tmp_path / "llm.csv"
    comparison_path = tmp_path / "comparison.csv"
    summary_path = tmp_path / "summary.md"

    pd.DataFrame(
        [
            {
                "placement_id": 1,
                "company_name": "Jet3 Holidays",
                "topic": "Travel blog",
                "safety_decision": "safe",
                "safety_confidence": "high",
                "risk_categories": "",
            },
            {
                "placement_id": 2,
                "company_name": "Jet3 Holidays",
                "topic": "Flight disasters",
                "safety_decision": "unsafe",
                "safety_confidence": "high",
                "risk_categories": "aviation_incident",
            },
        ]
    ).to_csv(rules_path, index=False)
    pd.DataFrame(
        [
            {
                "placement_id": 1,
                "llm_safety_decision": "safe",
                "llm_safety_confidence": "high",
                "llm_risk_categories": "",
                "llm_safety_rationale": "Looks fine.",
            },
            {
                "placement_id": 2,
                "llm_safety_decision": "review",
                "llm_safety_confidence": "medium",
                "llm_risk_categories": "aviation_incident",
                "llm_safety_rationale": "Needs review.",
            },
        ]
    ).to_csv(llm_path, index=False)

    comparison, summary = compare_llm_with_rules(
        rules_path=rules_path,
        llm_path=llm_path,
        comparison_output_path=comparison_path,
        summary_output_path=summary_path,
    )

    assert comparison["decision_match"].tolist() == [True, False]
    assert "Decision match rate: 50.0%" in summary
    assert comparison_path.exists()
    assert summary_path.exists()
