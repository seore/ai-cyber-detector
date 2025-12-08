import streamlit as st
import pandas as pd

from pathlib import Path
from detect import score_logs
from data_prep import save_processed
from config import PROCESSED_DATA_DIR

st.set_page_config(
    page_title="AI Cyber Log Anomaly Detector",
    layout="wide",
)

st.title("🛡️ AI Cyber Log Anomaly Detector")

st.markdown(
    """
Upload a CSV of security logs (timestamp, src_ip, username, event_type, status)  
and this app will score events for anomalies, compute user risk, and show quick insights.
"""
)

uploaded = st.file_uploader("Upload logs CSV", type=["csv"])

if uploaded is not None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = PROCESSED_DATA_DIR / "uploaded_for_detection.csv"
    df_raw = pd.read_csv(uploaded)
    save_processed(df_raw, tmp_path)

    with st.spinner("Scoring anomalies..."):
        events_df, user_risk_df = score_logs(tmp_path)

    st.subheader("Top Suspicious Events")
    st.dataframe(
        events_df.sort_values("anomaly_score", ascending=False)
        .head(50)[
            [
                "timestamp",
                "username",
                "src_ip",
                "event_type",
                "status",
                "country",
                "anomaly_score",
                "is_anomaly",
            ]
        ],
        use_container_width=True,
    )

    st.subheader("User Risk Scores")
    st.dataframe(user_risk_df.head(50), use_container_width=True)

    st.subheader("Events by Country (approx. heatmap)")
    country_counts = events_df["country"].fillna("unknown").value_counts().reset_index()
    country_counts.columns = ["country", "events"]
    st.bar_chart(country_counts.set_index("country"))
else:
    st.info("Upload a log CSV to get started.")
