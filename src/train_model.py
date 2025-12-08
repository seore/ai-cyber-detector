import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "historical_logs.csv"
MODEL_PATH = BASE_DIR / "models" / "anomaly_pipeline.joblib"


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Basic cleaning / timestamp features
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"] = df["timestamp"].dt.hour
        df["dayofweek"] = df["timestamp"].dt.dayofweek
        df = df.drop(columns=["timestamp"])

    return df


def build_pipeline(df: pd.DataFrame) -> Pipeline:
    # Simple heuristic: numeric vs non-numeric columns
    numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = df.select_dtypes(exclude=[np.number]).columns.tolist()

    numeric_transformer = Pipeline(
        steps=[
            ("scaler", StandardScaler())
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    # Isolation Forest for unsupervised anomaly detection
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,  
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


def main():
    print(f"Loading data from {DATA_PATH}")
    df = load_data(DATA_PATH)

    print("Building pipeline...")
    pipeline = build_pipeline(df)

    print("Training model (unsupervised)...")
    pipeline.fit(df) 

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved trained pipeline to {MODEL_PATH}")


if __name__ == "__main__":
    main()
