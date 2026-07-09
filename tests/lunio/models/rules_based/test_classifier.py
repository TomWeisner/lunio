from lunio.models.rules_based.classifier import Decision, score_placement


def test_jet3_flight_disaster_is_unsafe_with_enriched_signals() -> None:
    score = score_placement(
        {
            "url": "https://example.com/story/123",
            "company_name": "Jet3 Holidays",
            "topic": "Flight disasters (investigations)",
            "title": "Investigation into aircraft crash",
            "clicks": 100,
            "invalid_clicks": 1,
        },
        use_enriched_fields=True,
    )

    assert score.decision == Decision.UNSAFE
    assert "aviation_incident" in score.risk_categories


def test_url_only_unknown_content_goes_to_review() -> None:
    score = score_placement(
        {
            "url": "https://example.com/article/123456",
            "company_name": "Moonbucks Coffee",
            "clicks": 100,
            "invalid_clicks": 1,
        },
        use_enriched_fields=False,
    )

    assert score.decision == Decision.REVIEW
    assert "unknown_content" in score.risk_categories


def test_enriched_low_risk_topic_is_safe() -> None:
    score = score_placement(
        {
            "url": "https://example.com/one-pot-pasta",
            "company_name": "Moonbucks Coffee",
            "topic": "Cooking (one-pot pasta)",
            "title": "Easy one-pot pasta for busy weeknights",
            "clicks": 100,
            "invalid_clicks": 1,
        },
        use_enriched_fields=True,
    )

    assert score.decision == Decision.SAFE
