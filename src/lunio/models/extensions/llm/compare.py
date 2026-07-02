"""Compare LLM judge outputs with rule-based safety outputs.

Run from the project root with:

    poetry run python -m lunio.models.extensions.llm.compare
"""

import argparse
from pathlib import Path

import pandas as pd

from lunio.paths import REPORTS_DIR

RULES_OUTPUT_PATH = REPORTS_DIR / "scored_full_data.csv"
LLM_OUTPUT_PATH = REPORTS_DIR / "llm_scored_full_data.csv"
COMPARISON_OUTPUT_PATH = REPORTS_DIR / "llm_vs_rules_comparison.csv"
SUMMARY_OUTPUT_PATH = REPORTS_DIR / "llm_vs_rules_summary.md"


def compare_llm_with_rules(
    *,
    rules_path=RULES_OUTPUT_PATH,
    llm_path=LLM_OUTPUT_PATH,
    comparison_output_path=COMPARISON_OUTPUT_PATH,
    summary_output_path=SUMMARY_OUTPUT_PATH,
) -> tuple[pd.DataFrame, str]:
    """Compare rule-based decisions with LLM judge decisions and write reports."""

    rules = pd.read_csv(rules_path)
    llm = pd.read_csv(llm_path)
    comparison = rules[
        [
            "placement_id",
            "company_name",
            "topic",
            "safety_decision",
            "safety_confidence",
            "risk_categories",
        ]
    ].merge(
        llm[
            [
                "placement_id",
                "llm_safety_decision",
                "llm_safety_confidence",
                "llm_risk_categories",
                "llm_safety_rationale",
            ]
        ],
        on="placement_id",
        how="inner",
    )
    comparison["decision_match"] = (
        comparison["safety_decision"] == comparison["llm_safety_decision"]
    )

    comparison_output_path.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(comparison_output_path, index=False)

    summary = _build_summary(comparison)
    summary_output_path.write_text(summary, encoding="utf-8")
    return comparison, summary


def _build_summary(comparison: pd.DataFrame) -> str:
    total_rows = len(comparison)
    matched_rows = int(comparison["decision_match"].sum())
    match_rate = matched_rows / total_rows if total_rows else 0
    confusion = pd.crosstab(
        comparison["safety_decision"],
        comparison["llm_safety_decision"],
        rownames=["rules_decision"],
        colnames=["llm_decision"],
        dropna=False,
    )

    return "\n\n".join(
        [
            "# LLM vs Rules Comparison",
            f"- Compared rows: {total_rows:,}",
            f"- Matching decisions: {matched_rows:,}",
            f"- Decision match rate: {match_rate:.1%}",
            "## Decision Matrix",
            _to_markdown_table(confusion.reset_index()),
        ]
    )


def _to_markdown_table(dataframe: pd.DataFrame) -> str:
    headers = [str(column) for column in dataframe.columns]
    rows = [
        [str(value) for value in row]
        for row in dataframe.itertuples(index=False, name=None)
    ]
    separator = ["---"] * len(headers)
    table_rows = [headers, separator, *rows]
    return "\n".join("| " + " | ".join(row) + " |" for row in table_rows)


def main() -> None:
    """Write LLM-vs-rules comparison outputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", default=RULES_OUTPUT_PATH, type=str)
    parser.add_argument("--llm", default=LLM_OUTPUT_PATH, type=str)
    parser.add_argument("--comparison-output", default=COMPARISON_OUTPUT_PATH, type=str)
    parser.add_argument("--summary-output", default=SUMMARY_OUTPUT_PATH, type=str)
    args = parser.parse_args()

    comparison, _ = compare_llm_with_rules(
        rules_path=Path(args.rules),
        llm_path=Path(args.llm),
        comparison_output_path=Path(args.comparison_output),
        summary_output_path=Path(args.summary_output),
    )
    print(f"Compared {len(comparison)} rows and wrote {args.comparison_output}")


if __name__ == "__main__":
    main()
