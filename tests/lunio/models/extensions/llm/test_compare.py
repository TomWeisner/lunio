import pandas as pd

from lunio.models.extensions.llm.compare import compare_llm_with_rules


def test_compare_llm_with_rules_writes_comparison_and_html_report(tmp_path) -> None:
    rules_path = tmp_path / "rules.csv"
    llm_path = tmp_path / "llm.csv"
    comparison_path = tmp_path / "comparison.csv"
    html_path = tmp_path / "report.html"

    pd.DataFrame(
        [
            {
                "placement_id": 2,
                "company_name": "Jet3 Holidays",
                "topic": "Flight disasters",
                "url": "https://example.com/flight-disaster",
                "safety_decision": "unsafe",
                "safety_confidence": "high",
                "risk_categories": "aviation_incident",
                "matched_signals": "title:disaster->aviation_incident",
                "safety_rationale": (
                    "Unsafe for Jet3 Holidays: detected aviation_incident."
                ),
            },
            {
                "placement_id": 1,
                "company_name": "Jet3 Holidays",
                "topic": "Travel blog",
                "url": "https://example.com/travel",
                "safety_decision": "safe",
                "safety_confidence": "high",
                "risk_categories": "",
                "matched_signals": "",
                "safety_rationale": "No risk categories detected.",
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

    comparison = compare_llm_with_rules(
        rules_path=rules_path,
        llm_path=llm_path,
        comparison_output_path=comparison_path,
        html_output_path=html_path,
    )

    html_report = html_path.read_text(encoding="utf-8")
    assert comparison["decision_match"].tolist() == [False, True]
    assert comparison["url"].tolist() == [
        "https://example.com/flight-disaster",
        "https://example.com/travel",
    ]
    assert comparison_path.exists()
    assert html_path.exists()
    assert "<title>LLM vs Rules Report</title>" in html_report
    assert 'class="contents-nav"' in html_report
    assert 'href="#commentary"' in html_report
    assert 'id="decisions"' in html_report
    assert 'id="confidences"' in html_report
    assert 'id="discrepancies"' in html_report
    assert "Commentary" in html_report
    assert 'id="commentary"' in html_report
    assert "Productionising" in html_report
    assert 'id="raw-predictions"' in html_report
    assert "Prediction distribution by confidence" in html_report
    assert 'aria-label="Confidence matrix"' in html_report
    assert 'class="comparison-like-table"' in html_report
    assert 'class="expand-button"' in html_report
    assert 'id="topic-filter"' in html_report
    assert 'id="match-filter"' in html_report
    assert 'href="https://example.com/flight-disaster"' in html_report
    assert "Needs review." in html_report
    assert "Rules confidence" in html_report
    assert "Rules trigger evidence" in html_report
    assert "LLM confidence" in html_report
    assert comparison["rules_signal_explanations"].tolist() == [
        'matched "disaster" in title, triggering aviation_incident',
        "",
    ]
