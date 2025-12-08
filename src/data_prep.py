import pandas as pd
from pathlib import Path
from .config import REQUIRED_COLUMNS

def load_logs(path: Path) -> pd.DataFrame:
    """
    Load raw log CSV and ensure required columns exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(f"Log file is empty: {path}")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {path}: {missing}")

    # Parse timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # Fill NaNs in categorical fields
    for col in ["src_ip", "username", "event_type", "status"]:
        if col in df.columns:
            df[col] = df[col].fillna("unknown")

    return df


def save_processed(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
