import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OUT_PATH = DATA_DIR / "historical_logs.csv"

rows = [
    {
        "timestamp": "2025-01-01T10:00:00Z",
        "source_ip": "192.168.1.10",
        "dest_ip": "10.0.0.5",
        "dest_port": 443,
        "protocol": "TCP",
        "method": "GET",
        "status_code": 200,
        "bytes_sent": 512,
        "bytes_received": 2048,
        "event_type": "normal",
        "is_malicious": 0,
    },
    {
        "timestamp": "2025-01-01T10:10:00Z",
        "source_ip": "203.0.113.50",
        "dest_ip": "10.0.0.12",
        "dest_port": 22,
        "protocol": "TCP",
        "method": "SSH",
        "status_code": 401,
        "bytes_sent": 64,
        "bytes_received": 128,
        "event_type": "brute_force",
        "is_malicious": 1,
    },
]

df = pd.DataFrame(rows)
df.to_csv(OUT_PATH, index=False)
print(f"Saved dummy data to {OUT_PATH}")



