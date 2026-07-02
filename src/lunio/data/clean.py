"""Export placement workbook sheets to CSV.

Run from the project root with:

    poetry run python -m lunio.data.clean
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "placement_data.xlsx"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "clean"

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
