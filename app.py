import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "anomaly_pipeline.joblib"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def preprocess_uploaded(df: pd.DataFrame) -> pd.DataFrame:
    # Mirror the logic from train_model.load_data()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hour"] = df["timestamp"].dt.hour
        df["dayofweek"] = df["timestamp"].dt.dayofweek
        df = df.drop(columns=["timestamp"])
    return df


def main():
    st.set_page_config(
        page_title="AI Cyber Log Anomaly Detector",
        page_icon="🛡️",
        layout="wide",
    )

    st.title("🛡️ AI Cyber Log Anomaly Detector")
    st.write(
        "Upload security / access logs and let an Isolation Forest model detect anomalous events."
    )

    if not MODEL_PATH.exists():
        st.error(
            f"Model not found at `{MODEL_PATH}`.\n\n"
            "👉 Run `python src/train_model.py` first to train and save the model."
        )
        return

    model = load_model()

    uploaded_file = st.file_uploader(
        "Upload a log file (CSV)", type=["csv"]
    )

    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
        st.subheader("Preview of uploaded data")
        st.dataframe(df_raw.head())

        df = preprocess_uploaded(df_raw.copy())

        # Decision function gives anomaly score (lower = more anomalous)
        scores = model.decision_function(df)
        preds = model.predict(df)  # -1 = anomaly, 1 = normal

        df_results = df_raw.copy()
        df_results["anomaly_score"] = scores
        df_results["is_anomaly"] = np.where(preds == -1, True, False)

        st.subheader("Detection summary")
        total = len(df_results)
        anomalies = df_results["is_anomaly"].sum()
        st.write(f"Total events: **{total}**")
        st.write(f"Flagged anomalies: **{anomalies}**")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Anomaly score distribution")
            fig, ax = plt.subplots()
            ax.hist(df_results["anomaly_score"], bins=40)
            ax.set_xlabel("Anomaly score")
            ax.set_ylabel("Count")
            st.pyplot(fig)

        with col2:
            st.subheader("Top suspicious events")
            top_k = st.slider("Show top N anomalies", 5, 100, 20)
            top_anomalies = df_results.sort_values("anomaly_score").head(top_k)
            st.dataframe(top_anomalies)

        st.subheader("Download results")
        csv = df_results.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV with anomaly flags",
            csv,
            "anomaly_results.csv",
            "text/csv",
        )


if __name__ == "__main__":
    main()
