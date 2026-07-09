"""Shared project paths."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CLEAN_DATA_DIR = DATA_DIR / "clean"
REPORTS_DIR = PROJECT_ROOT / "reports"
