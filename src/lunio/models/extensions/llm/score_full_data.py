"""Score full_data.csv rows with the optional LLM placement safety judge.

Run from the project root with:

    OPENAI_API_KEY=... poetry run python -m lunio.models.extensions.llm.score_full_data
"""

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from lunio.models.extensions.llm.score_placement import (
    DEFAULT_OPENAI_MODEL,
    run_llm_judge,
)
from lunio.paths import CLEAN_DATA_DIR, REPORTS_DIR

FULL_DATA_PATH = CLEAN_DATA_DIR / "full_data.csv"
LLM_OUTPUT_PATH = REPORTS_DIR / "llm_scored_full_data.csv"


def score_full_data_with_llm(
    *,
    input_path=FULL_DATA_PATH,
    output_path=LLM_OUTPUT_PATH,
    model: str = DEFAULT_OPENAI_MODEL,
    limit: int | None = None,
    show_progress: bool = True,
    skip_completed: bool = True,
) -> pd.DataFrame:
    """Score full_data rows with the LLM judge and write the combined output."""

    data = pd.read_csv(input_path)
    if limit is not None:
        data = data.head(limit)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    existing_output = (
        _read_existing_output(output_path) if skip_completed else pd.DataFrame()
    )
    completed_placement_ids = (
        _completed_placement_ids(existing_output) if skip_completed else set()
    )
    if completed_placement_ids:
        data = data[~data["placement_id"].isin(completed_placement_ids)]

    total_rows = len(data)
    if show_progress:
        print(
            f"Scoring {total_rows:,} row(s) with {model}..."
            f" Skipping {len(completed_placement_ids):,} already-scored row(s)."
        )

    llm_results = []
    for row_number, (_, row) in enumerate(data.iterrows(), start=1):
        placement = row.to_dict()
        if show_progress:
            print(
                "Scoring "
                f"{row_number:,}/{total_rows:,}: "
                f"placement_id={placement.get('placement_id', '')}, "
                f"advertiser={placement.get('company_name', '')}, "
                f"topic={placement.get('topic', '')}"
            )

        result = _flatten_llm_result(run_llm_judge(placement, model=model))
        llm_results.append(result)
        scored_so_far = _combine_outputs(existing_output, data, llm_results)
        scored_so_far.to_csv(output_path, index=False)

        if show_progress:
            print(
                "Completed "
                f"{row_number:,}/{total_rows:,}: "
                f"decision={result['llm_safety_decision']}, "
                f"confidence={result['llm_safety_confidence']}. "
                f"Checkpoint written to {output_path}"
            )

    scored = _combine_outputs(existing_output, data, llm_results)

    scored.to_csv(output_path, index=False)
    if show_progress:
        print(f"Wrote {len(scored):,} LLM-scored row(s) to {output_path}")
    return scored


def _read_existing_output(output_path: Path) -> pd.DataFrame:
    if not output_path.exists():
        return pd.DataFrame()
    return pd.read_csv(output_path)


def _completed_placement_ids(existing_output: pd.DataFrame) -> set[Any]:
    if existing_output.empty or "placement_id" not in existing_output:
        return set()
    completed_rows = existing_output[
        existing_output.get("llm_safety_decision", pd.Series(dtype=str)).notna()
    ]
    return set(completed_rows["placement_id"].tolist())


def _combine_outputs(
    existing_output: pd.DataFrame,
    data: pd.DataFrame,
    llm_results: list[dict[str, Any]],
) -> pd.DataFrame:
    current_data = data.head(len(llm_results)).reset_index(drop=True)
    current_output = pd.concat(
        [current_data, pd.DataFrame(llm_results)],
        axis=1,
    )
    if existing_output.empty:
        return current_output
    return pd.concat([existing_output, current_output], ignore_index=True)


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
    parser.add_argument(
        "--no-skip-completed",
        action="store_false",
        dest="skip_completed",
        help=(
            "Re-score rows even if the output CSV already contains an LLM "
            "decision for their placement_id. By default completed rows are skipped."
        ),
    )
    args = parser.parse_args()

    scored = score_full_data_with_llm(
        input_path=Path(args.input),
        output_path=Path(args.output),
        model=args.model,
        limit=args.limit,
        skip_completed=args.skip_completed,
    )
    print(f"Finished LLM full-data scoring for {len(scored):,} row(s).")


if __name__ == "__main__":
    main()
