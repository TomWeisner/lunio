"""Compare LLM judge outputs with rule-based safety outputs.

Run from the project root with:

    poetry run python -m lunio.models.extensions.llm.compare
"""

import argparse
from pathlib import Path

import pandas as pd

from lunio.models.extensions.llm.compare_html import build_html_report
from lunio.paths import REPORTS_DIR

RULES_OUTPUT_PATH = REPORTS_DIR / "scored_full_data.csv"
LLM_OUTPUT_PATH = REPORTS_DIR / "llm_scored_full_data.csv"
COMPARISON_OUTPUT_PATH = REPORTS_DIR / "llm_vs_rules_comparison.csv"
HTML_OUTPUT_PATH = REPORTS_DIR / "llm_vs_rules_report.html"


def _build_rules_signal_explanations(matched_signals: object) -> str:
    """Return a human-readable summary of rule trigger evidence."""

    if pd.isna(matched_signals):
        return ""

    raw_signals = [signal.strip() for signal in str(matched_signals).split(";")]
    descriptions = [
        description
        for signal in raw_signals
        if signal
        for description in [_describe_rules_signal(signal)]
        if description
    ]
    return "; ".join(descriptions)


def _describe_rules_signal(signal: str) -> str:
    """Describe one rules-engine signal in plainer language."""

    if "->" in signal and ":" in signal:
        source_and_term, category = signal.split("->", 1)
        source, term = source_and_term.split(":", 1)
        if source == "invalid_click_rate":
            return f"invalid click rate {term} triggered {category}"
        return f'matched "{term}" in {source}, triggering {category}'

    if signal.startswith("raw-url-only:"):
        return signal.replace("raw-url-only:", "raw URL only: ", 1)

    return signal


def compare_llm_with_rules(
    *,
    rules_path=RULES_OUTPUT_PATH,
    llm_path=LLM_OUTPUT_PATH,
    comparison_output_path=COMPARISON_OUTPUT_PATH,
    html_output_path=HTML_OUTPUT_PATH,
) -> pd.DataFrame:
    """Compare rule-based decisions with LLM judge decisions and write reports."""

    rules = pd.read_csv(rules_path)
    llm = pd.read_csv(llm_path)
    comparison = rules[
        [
            "placement_id",
            "company_name",
            "topic",
            "url",
            "safety_decision",
            "safety_confidence",
            "risk_categories",
            "matched_signals",
            "safety_rationale",
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
    comparison["rules_signal_explanations"] = comparison["matched_signals"].apply(
        _build_rules_signal_explanations
    )

    comparison_output_path.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(comparison_output_path, index=False)

    html_report = build_html_report(
        comparison,
        rules_count=len(rules),
        llm_count=len(llm),
        comparison_output_path=comparison_output_path,
    )
    html_output_path.write_text(html_report, encoding="utf-8")
    return comparison


def main() -> None:
    """Write LLM-vs-rules comparison outputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", default=RULES_OUTPUT_PATH, type=str)
    parser.add_argument("--llm", default=LLM_OUTPUT_PATH, type=str)
    parser.add_argument("--comparison-output", default=COMPARISON_OUTPUT_PATH, type=str)
    parser.add_argument("--html-output", default=HTML_OUTPUT_PATH, type=str)
    args = parser.parse_args()

    comparison = compare_llm_with_rules(
        rules_path=Path(args.rules),
        llm_path=Path(args.llm),
        comparison_output_path=Path(args.comparison_output),
        html_output_path=Path(args.html_output),
    )
    print(
        f"Compared {len(comparison)} rows and wrote "
        f"{args.comparison_output} and {args.html_output}"
    )


if __name__ == "__main__":
    main()
