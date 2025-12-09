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

st.title("AI Cyber Log Anomaly Detector")

st.markdown(
    """
Upload a CSV of security logs (`timestamp`, `src_ip`, `username`, `event_type`, `status`)  
and this app will score events for anomalies, compute user risk, and show quick insights.
"""
)

uploaded = st.file_uploader("Upload logs CSV", type=["csv"])

HIGH_RISK_THRESHOLD = 0.9

if uploaded is not None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = PROCESSED_DATA_DIR / "uploaded_for_detection.csv"

    df_raw = pd.read_csv(uploaded)
    save_processed(df_raw, tmp_path)

    with st.spinner("Scoring anomalies..."):
        events_df, user_risk_df = score_logs(tmp_path)

    # Scored events table
    st.subheader("📊 Scored Events")
    base_cols = [
        "timestamp",
        "username",
        "src_ip",
        "event_type",
        "status",
        "country",
        "anomaly_score",
        "is_anomaly",
    ]
    scored_cols = [c for c in base_cols if c in events_df.columns]

    st.dataframe(
        events_df.sort_values("anomaly_score", ascending=False).head(200)[scored_cols],
        use_container_width=True,
    )

    # High-risk alerts
    st.subheader("🚨 High-Risk Alerts")

    high_risk_events = events_df[events_df["anomaly_score"] >= HIGH_RISK_THRESHOLD].copy()

    if high_risk_events.empty:
        st.success(
            f"No events above the high-risk threshold (anomaly_score ≥ {HIGH_RISK_THRESHOLD}). 🎉"
        )
    else:
        st.warning(
            f"{len(high_risk_events)} high-risk events detected (anomaly_score ≥ {HIGH_RISK_THRESHOLD})."
        )
        alert_cols = [
            "timestamp",
            "username",
            "src_ip",
            "event_type",
            "status",
            "country",
            "anomaly_score",
        ]
        alert_cols = [c for c in alert_cols if c in high_risk_events.columns]

        st.dataframe(
            high_risk_events[alert_cols].sort_values(
                "anomaly_score", ascending=False
            ),
            use_container_width=True,
        )

    # Top risky users 
    st.subheader("👤 Top Risky Users")

    if user_risk_df is not None and not user_risk_df.empty:
        st.dataframe(
            user_risk_df.sort_values("avg_score", ascending=False),
            use_container_width=True,
        )
    else:
        if "username" in events_df.columns:
            user_risk = (
                events_df.groupby("username")
                .agg(
                    avg_score=("anomaly_score", "mean"),
                    max_score=("anomaly_score", "max"),
                    event_count=("anomaly_score", "count"),
                    high_risk_events=(
                        "anomaly_score",
                        lambda s: (s >= HIGH_RISK_THRESHOLD).sum(),
                    ),
                )
                .reset_index()
                .sort_values("avg_score", ascending=False)
            )
            st.dataframe(user_risk, use_container_width=True)
        else:
            st.info("No `username` column found, cannot compute per-user risk.")

    # Country breakdown
    st.subheader("🌍 Events by Country")

    if "country" in events_df.columns:
        country_counts = (
            events_df["country"]
            .fillna("unknown")
            .value_counts()
            .reset_index()
        )
        country_counts.columns = ["country", "events"]

        st.bar_chart(
            country_counts.set_index("country")["events"],
            use_container_width=True,
        )
    else:
        st.info("No `country` column found in the data, skipping country breakdown.")
else:
    st.info("Upload a log CSV to get started.")
