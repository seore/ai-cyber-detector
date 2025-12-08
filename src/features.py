from typing import Tuple

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


CATEGORICAL_COLS = ["event_type", "status", "country"]
NUMERIC_COLS = [
    "hour",
    "user_event_count",
    "user_failed_count",
    "user_unique_ips",
]


def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create useful features for anomaly detection:
    - hour of day
    - per-user stats: event count, failed count, unique IPs
    """
    df = df.copy()

    # Time-based features
    df["hour"] = df["timestamp"].dt.hour

    # User aggregation
    user_group = df.groupby("username")
    df["user_event_count"] = user_group["username"].transform("count")
    df["user_failed_count"] = user_group["status"].transform(
        lambda s: (s.str.lower() == "failure").sum()
    )
    df["user_unique_ips"] = user_group["src_ip"].transform("nunique")

    # Replace NaNs
    df["country"] = df["country"].fillna("unknown")

    return df


def build_feature_pipeline() -> Pipeline:
    """
    Create a preprocessing pipeline that:
    - one-hot encodes categorical columns
    - passes numeric columns through
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLS),
            ("num", "passthrough", NUMERIC_COLS),
        ]
    )

    pipeline = Pipeline(steps=[("preprocessor", preprocessor)])
    return pipeline


def get_feature_columns() -> Tuple[list, list]:
    """
    Return (categorical_cols, numeric_cols) so train/detect scripts stay in sync.
    """
    return CATEGORICAL_COLS, NUMERIC_COLS
