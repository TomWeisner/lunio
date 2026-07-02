"""OpenAI runner for the optional LLM placement safety judge.

Run from the project root with:

    OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.runner \
        placement.json
"""

import argparse
import json
import os
from typing import Any
from urllib import error, request

from lunio.models.extensions.llm.judge import (
    SAFETY_JUDGE_JSON_SCHEMA,
    build_llm_judge_prompt,
)

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"


def run_llm_judge(
    placement: dict[str, Any],
    *,
    model: str = DEFAULT_OPENAI_MODEL,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Call OpenAI with the judge prompt and return the parsed JSON decision."""

    resolved_api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not resolved_api_key:
        raise ValueError("OPENAI_API_KEY must be set to run the LLM judge.")

    payload = {
        "model": model,
        "input": build_llm_judge_prompt(placement),
        "text": {
            "format": {
                "type": "json_schema",
                "name": "placement_safety_judge",
                "schema": SAFETY_JUDGE_JSON_SCHEMA,
                "strict": True,
            }
        },
    }
    response_body = _post_openai_json(payload, api_key=resolved_api_key)
    response_text = _extract_response_text(response_body)
    return json.loads(response_text)


def _post_openai_json(payload: dict[str, Any], *, api_key: str) -> dict[str, Any]:
    request_body = json.dumps(payload).encode("utf-8")
    openai_request = request.Request(
        OPENAI_RESPONSES_URL,
        data=request_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(openai_request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        msg = f"OpenAI API request failed with status {exc.code}: {details}"
        raise RuntimeError(msg) from exc


def _extract_response_text(response_body: dict[str, Any]) -> str:
    for output_item in response_body.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") == "output_text":
                return str(content_item.get("text", ""))

    raise ValueError("OpenAI response did not include output_text content.")


def main() -> None:
    """Run the LLM judge for a placement JSON file."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "placement_json",
        help="Path to a JSON file containing one placement",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_OPENAI_MODEL,
        help=f"OpenAI model to use. Defaults to {DEFAULT_OPENAI_MODEL}.",
    )
    args = parser.parse_args()

    with open(args.placement_json, encoding="utf-8") as placement_file:
        placement = json.load(placement_file)

    decision = run_llm_judge(placement, model=args.model)
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
