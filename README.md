# AI Cyber Log Anomaly Detector

An AI-powered anomaly detection tool for security logs, with an interactive Streamlit dashboard.

This project ingests authentication / access logs, engineers security-focused features, trains an unsupervised anomaly detection model, and surfaces suspicious activity with risk scores, alerts, and analyst-friendly views.

---

## 🔍 What this project does

- Loads security log data from CSV (e.g. auth / VPN / access logs)
- Cleans and validates the data (required columns, timestamp parsing, etc.)
- Engineers features such as:
  - Hour of day
  - Per-user event volume
  - Failed login counts
  - Unique IPs per user
- Trains an anomaly detection model on historical logs
- Scores new logs with an **anomaly_score**
- Exposes an interactive **Streamlit dashboard** where you can:
  - Upload a CSV of logs
  - See anomaly scores per event
  - View **high-risk alerts**
  - See **top risky users** based on aggregated risk
  - Explore basic summaries (IPs / countries / events)

This is NOT meant to replace a SIEM, but to show how ML can help a security analyst quickly flag suspicious behavior.

---

## 🧱 Tech Stack

- **Language:** Python 3
- **ML / Data:**
  - `pandas`
  - `scikit-learn` (e.g. IsolationForest or similar anomaly model)
- **App / Visualisation:** `streamlit`
- **Model persistence:** `joblib`
- **Project structure:** simple modular layout under `src/` for training, detection, features, and dashboard.
