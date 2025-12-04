# config.py

from pathlib import Path
import os

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "Images"
PARQUET_DIR = DATA_DIR / "parquet"
EXPORT_DIR = BASE_DIR / "exports"

# -----------------------------
# STREAMLIT SETTINGS
# -----------------------------
APP_TITLE = "Club Cannon Database"
APP_ICON = IMAGES_DIR / "club-cannon-icon-black.png"
LAYOUT = "wide"
SIDEBAR_STATE = "collapsed"


# -----------------------------
# DATE CONSTANTS
# -----------------------------
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

MONTHS_ALL_OPTION = ["All"] + MONTHS
YEARS = [2022, 2023, 2024, 2025, 2026]
MONTHS_X = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# -----------------------------
# ENVIRONMENT SETTINGS
# -----------------------------
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"



