import pytest

from lunio.models.extensions.llm import runner
from lunio.models.extensions.llm.runner import _extract_response_text, run_llm_judge


def test_extract_response_text_reads_first_output_text() -> None:
    response_body = {
        "output": [
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": '{"decision":"review"}',
                    }
                ]
            }
        ]
    }

    assert _extract_response_text(response_body) == '{"decision":"review"}'


def test_run_llm_judge_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        run_llm_judge({"company_name": "Jet3 Holidays"})


def test_main_reads_placement_file_and_prints_decision(
    tmp_path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    placement_path = tmp_path / "placement.json"
    placement_path.write_text(
        '{"company_name": "Jet3 Holidays", "url": "https://example.com"}',
        encoding="utf-8",
    )

    def fake_run_llm_judge(placement, *, model):
        assert placement["company_name"] == "Jet3 Holidays"
        assert model == runner.DEFAULT_OPENAI_MODEL
        return {"decision": "review"}

    monkeypatch.setattr(runner, "run_llm_judge", fake_run_llm_judge)
    monkeypatch.setattr(
        "sys.argv",
        ["runner", str(placement_path)],
    )

    runner.main()

    assert '"decision": "review"' in capsys.readouterr().out
