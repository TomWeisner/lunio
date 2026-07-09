import pandas as pd

from lunio.models.extensions.llm import score_full_data
from lunio.models.extensions.llm.score_full_data import _flatten_llm_result


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


def test_score_full_data_with_llm_writes_output(tmp_path, monkeypatch) -> None:
    input_path = tmp_path / "full_data.csv"
    output_path = tmp_path / "llm_scored_full_data.csv"
    pd.DataFrame(
        [
            {
                "placement_id": 1,
                "company_name": "Plush Cosmetics",
                "topic": "Tabagism / quitting smoking",
            }
        ]
    ).to_csv(input_path, index=False)

    def fake_run_llm_judge(placement, *, model):
        assert placement["placement_id"] == 1
        assert model == "test-model"
        return {
            "decision": "unsafe",
            "confidence": "high",
            "risk_categories": [],
            "rationale": "Test rationale.",
            "missing_evidence": [],
        }

    monkeypatch.setattr(score_full_data, "run_llm_judge", fake_run_llm_judge)

    scored = score_full_data.score_full_data_with_llm(
        input_path=input_path,
        output_path=output_path,
        model="test-model",
        show_progress=False,
    )

    assert output_path.exists()
    assert scored["placement_id"].tolist() == [1]
    assert scored["llm_safety_decision"].tolist() == ["unsafe"]
