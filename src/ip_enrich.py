from typing import Optional, Dict

import requests
import pandas as pd

from .config import IPINFO_TOKEN


def enrich_ip_ipinfo(ip: str) -> Dict[str, Optional[str]]:
    """
    Enrich a single IP using ipinfo.io.
    Requires IPINFO_TOKEN env var. Falls back to 'unknown' if not set / error.
    """
    if not IPINFO_TOKEN:
        return {
            "ip": ip,
            "country": None,
            "region": None,
            "city": None
        }

    try:
        resp = requests.get(
            f"https://ipinfo.io/{ip}",
            params={"token": IPINFO_TOKEN},
            timeout=3,
        )
        if resp.status_code != 200:
            return {"ip": ip, "country": None, "region": None, "city": None}

        data = resp.json()
        return {
            "ip": ip,
            "country": data.get("country"),
            "region": data.get("region"),
            "city": data.get("city"),
        }
    except Exception:
        return {"ip": ip, "country": None, "region": None, "city": None}


def enrich_dataframe_ips(df: pd.DataFrame, ip_column: str = "src_ip") -> pd.DataFrame:
    """
    Deduplicate IPs and enrich, then merge back onto the dataframe.
    """
    unique_ips = df[ip_column].dropna().unique().tolist()
    records = []

    for ip in unique_ips:
        rec = enrich_ip_ipinfo(ip)
        records.append(rec)

    geo_df = pd.DataFrame(records)
    merged = df.merge(geo_df, how="left", left_on=ip_column, right_on="ip")
    merged.drop(columns=["ip"], inplace=True)

    return merged
