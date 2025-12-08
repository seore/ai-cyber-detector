from pathlib import Path
from typing import Tuple

import joblib
import pandas as pd

from .config import MODEL_PATH
from .data_prep import load_logs
from .ip_enrich import enrich_dataframe_ips
from .features import add_basic_features, get_feature_columns


def load_trained_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}. Train it first.")
    bundle = joblib.load(MODEL_PATH)
    return bundle["model"], bundle["pipeline"], bundle["feature_columns"]


def score_logs(path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Score a batch of logs and return:
    - events_df: original logs + anomaly_score + is_anomaly
    - user_risk_df: aggregated per-user risk scores
    """
    print(f"Loading logs from {path}...")
    df = load_logs(path)

    model, pipeline, feature_cols = load_trained_model()

    print("Enriching IPs...")
    df = enrich_dataframe_ips(df)
    df = add_basic_features(df)

    cat_cols, num_cols = get_feature_columns()
    used_cols = cat_cols + num_cols

    X = pipeline.transform(df)
    raw_scores = model.decision_function(X)  # higher = more normal

    # Convert to anomaly-like score (0 to 1; 1=most anomalous-ish)
    # Normalise by rank
    scores_series = pd.Series(raw_scores)
    anomaly_score = 1 - scores_series.rank(pct=True)

    df["anomaly_score"] = anomaly_score
    df["is_anomaly"] = anomaly_score > 0.95  # threshold; tweak as needed

    # User risk = average anomaly_score + boosts for high anomaly counts
    user_group = df.groupby("username")
    user_risk = user_group["anomaly_score"].mean().to_frame("avg_anomaly_score")
    user_risk["anomaly_count"] = user_group["is_anomaly"].sum()
    user_risk["total_events"] = user_group["anomaly_score"].count()
    user_risk["risk_score"] = (
        user_risk["avg_anomaly_score"] * 0.7
        + (user_risk["anomaly_count"] / user_risk["total_events"].clip(lower=1)) * 0.3
    )
    user_risk = user_risk.sort_values("risk_score", ascending=False).reset_index()

    return df, user_risk


if __name__ == "__main__":
    # Example usage:
    test_path = Path("data/processed/historical_logs.csv")
    events, users = score_logs(test_path)
    print("Top 10 suspicious events:")
    print(events.sort_values("anomaly_score", ascending=False).head(10)[
        ["timestamp", "username", "src_ip", "event_type", "status", "anomaly_score", "is_anomaly"]
    ])
    print("\nTop 10 risky users:")
    print(users.head(10))
