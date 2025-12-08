import os
from pathlib import Path

# Base project directory (root of the repo)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Default training dataset (after you preprocess / copy a real log CSV here)
TRAINING_DATA_PATH = PROCESSED_DATA_DIR / "historical_logs.csv"

# Models
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODELS_DIR / "isolation_forest.joblib"

# IP enrichment / geo
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")  # optional, for ipinfo API

# Columns we expect in logs (you can adapt to your dataset)
REQUIRED_COLUMNS = [
    "timestamp",   # datetime string
    "src_ip",      # source IP address
    "username",    # user / account name
    "event_type",  # e.g. "login", "file_access"
    "status"       # e.g. "success", "failure"
]
