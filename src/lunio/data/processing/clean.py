"""Export placement workbook sheets to CSV.

Run from the project root with:

    poetry run python -m lunio.data.processing.clean
"""

from pathlib import Path

import pandas as pd

from lunio.paths import CLEAN_DATA_DIR, DATA_DIR

RAW_DATA_PATH = DATA_DIR / "raw" / "placement_data.xlsx"
PROCESSED_DATA_DIR = CLEAN_DATA_DIR

SHEETS_TO_OUTPUTS = {
    "raw data": "raw_data.csv",
    "full data": "full_data.csv",
}


def export_placement_data_to_csv(
    source_path: Path = RAW_DATA_PATH,
    output_dir: Path = PROCESSED_DATA_DIR,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for sheet_name, output_filename in SHEETS_TO_OUTPUTS.items():
        dataframe = pd.read_excel(source_path, sheet_name=sheet_name)
        dataframe.to_csv(output_dir / output_filename, index=False)


if __name__ == "__main__":
    export_placement_data_to_csv()
