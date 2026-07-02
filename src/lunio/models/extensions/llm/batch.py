"""Batch runner for the optional LLM placement safety judge.

Run from the project root with:

    OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.batch
"""

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from lunio.models.extensions.llm.runner import DEFAULT_OPENAI_MODEL, run_llm_judge
from lunio.paths import CLEAN_DATA_DIR, REPORTS_DIR

FULL_DATA_PATH = CLEAN_DATA_DIR / "full_data.csv"
LLM_OUTPUT_PATH = REPORTS_DIR / "llm_scored_full_data.csv"


def score_full_data_with_llm(
    *,
    input_path=FULL_DATA_PATH,
    output_path=LLM_OUTPUT_PATH,
    model: str = DEFAULT_OPENAI_MODEL,
    limit: int | None = None,
) -> pd.DataFrame:
    """Score full_data rows with the LLM judge and write the combined output."""

    data = pd.read_csv(input_path)
    if limit is not None:
        data = data.head(limit)

    llm_results = [
        _flatten_llm_result(run_llm_judge(row.to_dict(), model=model))
        for _, row in data.iterrows()
    ]
    scored = pd.concat([data.reset_index(drop=True), pd.DataFrame(llm_results)], axis=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_path, index=False)
    return scored


def _flatten_llm_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "llm_safety_decision": result.get("decision", ""),
        "llm_safety_confidence": result.get("confidence", ""),
        "llm_risk_categories": ";".join(result.get("risk_categories", [])),
        "llm_safety_rationale": result.get("rationale", ""),
        "llm_missing_evidence": ";".join(result.get("missing_evidence", [])),
        "llm_raw_response": json.dumps(result, sort_keys=True),
    }


def main() -> None:
    """Run the LLM judge across rows in full_data.csv."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default=FULL_DATA_PATH,
        type=str,
        help=f"Input CSV path. Defaults to {FULL_DATA_PATH}.",
    )
    parser.add_argument(
        "--output",
        default=LLM_OUTPUT_PATH,
        type=str,
        help=f"Output CSV path. Defaults to {LLM_OUTPUT_PATH}.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_OPENAI_MODEL,
        help=f"OpenAI model to use. Defaults to {DEFAULT_OPENAI_MODEL}.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional row limit for smoke tests before scoring the full dataset.",
    )
    args = parser.parse_args()

    scored = score_full_data_with_llm(
        input_path=Path(args.input),
        output_path=Path(args.output),
        model=args.model,
        limit=args.limit,
    )
    print(f"Wrote {len(scored)} LLM-scored rows to {args.output}")


if __name__ == "__main__":
    main()
