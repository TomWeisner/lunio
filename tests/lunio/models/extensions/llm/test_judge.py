from lunio.models.extensions.llm.judge import build_llm_judge_prompt


def test_llm_judge_prompt_includes_advertiser_policy() -> None:
    prompt = build_llm_judge_prompt(
        {
            "company_name": "Jet3 Holidays",
            "url": "https://example.com/flight-crash",
            "title": "Flight crash investigation",
            "topic": "Flight disasters (investigations)",
        }
    )

    assert "Jet3 Holidays" in prompt
    assert "aviation_incident" in prompt
    assert "Return only JSON" in prompt
