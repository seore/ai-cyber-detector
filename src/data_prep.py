import pandas as pd
from pathlib import Path
from .config import REQUIRED_COLUMNS

# Aliases for different possible column names in real log datasets
COLUMN_ALIASES = {
    "timestamp": ["timestamp", "time", "date", "datetime", "event_time"],
    "src_ip": ["src_ip", "source_ip", "ip", "client_ip", "src"],
    "username": ["username", "user", "account", "user_name", "principal"],
    "event_type": ["event_type", "event", "action", "activity"],
    "status": ["status", "result", "outcome", "success", "failure_flag"],
}


def _standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Try to map various real-world column names to our standard internal names.

    If an alias is found, rename that column.
    """
    df = df.copy()
    lower_map = {c.lower(): c for c in df.columns}

    rename_map = {}

    for std_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias.lower() in lower_map:
                actual_col = lower_map[alias.lower()]
                rename_map[actual_col] = std_name
                break  # stop at the first match

    if rename_map:
        df = df.rename(columns=rename_map)

    return df


def load_logs(path: Path) -> pd.DataFrame:
    """
    Load raw log CSV and ensure we have usable columns.

    Behaviour:
    - 'timestamp' is required; if we can't find a reasonable column, raise an error.
    - 'src_ip', 'username', 'event_type', 'status' are optional but recommended.
      If missing, we create them with default values so the pipeline still runs.
    """
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError(f"Log file is empty: {path}")

    # Try to automatically map column aliases to our standard names
    df = _standardise_columns(df)

    # Ensure we have at least a timestamp column
    if "timestamp" not in df.columns:
        raise ValueError(
            f"No usable timestamp column found in {path}. "
            f"Tried aliases: {COLUMN_ALIASES['timestamp']}"
        )

    # Parse timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # For all other required columns, if still missing, create defaults
    for col in REQUIRED_COLUMNS:
        if col == "timestamp":
            continue  # already handled

        if col not in df.columns:
            # Create a sensible default column
            if col == "src_ip":
                default_value = "0.0.0.0"
            elif col in ("username", "event_type", "status"):
                default_value = "unknown"
            else:
                default_value = "unknown"

            print(
                f"[WARN] Column '{col}' not found in {path}. "
                f"Creating it with default value '{default_value}'. "
                f"For better results, map your real column to '{col}'."
            )
            df[col] = default_value

    # Final safety: fill NaNs in key categorical fields
    for col in ["src_ip", "username", "event_type", "status"]:
        if col in df.columns:
            df[col] = df[col].fillna("unknown")

    return df


def save_processed(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
