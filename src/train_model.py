import joblib
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest

from src.config import TRAINING_DATA_PATH, MODEL_PATH
from src.data_prep import load_logs
from .ip_enrich import enrich_dataframe_ips
from src.features import add_basic_features, build_feature_pipeline, get_feature_columns


def train_model(df: pd.DataFrame) -> None:
    """
    Train IsolationForest on engineered features and save model + pipeline.
    """
    print("Enriching IPs with geo data (if IPINFO_TOKEN set)...")
    df = enrich_dataframe_ips(df)

    print("Adding engineered features...")
    df = add_basic_features(df)

    cat_cols, num_cols = get_feature_columns()
    used_cols = cat_cols + num_cols

    print("Building feature pipeline...")
    feature_pipeline = build_feature_pipeline()
    X = feature_pipeline.fit_transform(df)

    print("Training IsolationForest...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.01,   
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)

    print(f"Saving model and feature pipeline to {MODEL_PATH}...")
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "pipeline": feature_pipeline,
            "feature_columns": used_cols,
        },
        MODEL_PATH,
    )
    print("Training complete.")


def main():
    data_path = Path(TRAINING_DATA_PATH)
    print(f"Loading training data from {data_path}...")
    df = load_logs(data_path)
    train_model(df)


if __name__ == "__main__":
    main()
