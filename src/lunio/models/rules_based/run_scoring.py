"""Score placement data and write CSV outputs.

Run from the project root with:

    poetry run python -m lunio.models.rules_based.run_scoring
"""

import pandas as pd

from lunio.models.rules_based.classifier import score_dataframe
from lunio.paths import CLEAN_DATA_DIR, REPORTS_DIR

RAW_INPUT_PATH = CLEAN_DATA_DIR / "raw_data.csv"
FULL_INPUT_PATH = CLEAN_DATA_DIR / "full_data.csv"
RAW_OUTPUT_PATH = REPORTS_DIR / "scored_raw_data.csv"
ENRICHED_OUTPUT_PATH = REPORTS_DIR / "scored_full_data.csv"


def run_scoring() -> None:
    """Create scored raw-only and enriched placement outputs."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_data = pd.read_csv(RAW_INPUT_PATH)
    full_data = pd.read_csv(FULL_INPUT_PATH)

    score_dataframe(raw_data, use_enriched_fields=False).to_csv(
        RAW_OUTPUT_PATH,
        index=False,
    )
    score_dataframe(full_data, use_enriched_fields=True).to_csv(
        ENRICHED_OUTPUT_PATH,
        index=False,
    )


if __name__ == "__main__":
    run_scoring()
