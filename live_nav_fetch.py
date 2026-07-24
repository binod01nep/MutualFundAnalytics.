"""
============================================================
Capstone Project I — Mutual Fund Analytics
Day 1: Live NAV Fetch
File   : live_nav_fetch.py
Author : bcb4314
Purpose: Fetch live NAV data from mfapi.in for HDFC Top 100
         Direct (Task 4) and 5 key large-cap schemes (Task 5).
         Parse JSON responses and save as raw CSVs.
============================================================
"""

import os
import time
import json
import requests
import pandas as pd
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
RAW_DIR   = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

SEPARATOR = "=" * 70

# ── Scheme registry ───────────────────────────────────────────────────────────
# Task 4: HDFC Top 100 Direct
HDFC_TOP_100 = {
    "scheme_code": 125497,
    "scheme_name": "HDFC Top 100 Direct",
}

# Task 5: 5 Key large-cap schemes
KEY_SCHEMES = [
    {"scheme_code": 119551, "scheme_name": "SBI Bluechip Direct"},
    {"scheme_code": 120503, "scheme_name": "ICICI Prudential Bluechip Direct"},
    {"scheme_code": 118632, "scheme_name": "Nippon India Large Cap Direct"},
    {"scheme_code": 119092, "scheme_name": "Axis Bluechip Direct"},
    {"scheme_code": 120841, "scheme_name": "Kotak Bluechip Direct"},
]

BASE_URL   = "https://api.mfapi.in/mf/{scheme_code}"
TIMEOUT    = 15   # seconds
RETRY_MAX  = 3
RETRY_WAIT = 2    # seconds between retries


# ─────────────────────────────────────────────────────────────────────────────
# Fetch helpers
# ─────────────────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def fetch_nav(scheme_code: int) -> dict | None:
    """
    GET https://api.mfapi.in/mf/<scheme_code>
    Returns the full parsed JSON dict or None on failure.
    Implements simple retry logic.
    """
    url = BASE_URL.format(scheme_code=scheme_code)
    for attempt in range(1, RETRY_MAX + 1):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"    [HTTP Error] {e} (attempt {attempt}/{RETRY_MAX})")
        except requests.exceptions.ConnectionError:
            print(f"    [Connection Error] Cannot reach {url} (attempt {attempt}/{RETRY_MAX})")
        except requests.exceptions.Timeout:
            print(f"    [Timeout] Request timed out (attempt {attempt}/{RETRY_MAX})")
        except requests.exceptions.RequestException as e:
            print(f"    [Request Error] {e} (attempt {attempt}/{RETRY_MAX})")
        except json.JSONDecodeError:
            print(f"    [Parse Error] Response is not valid JSON (attempt {attempt}/{RETRY_MAX})")

        if attempt < RETRY_MAX:
            time.sleep(RETRY_WAIT)

    return None


def parse_and_save(data: dict, scheme_name: str, scheme_code: int) -> pd.DataFrame | None:
    """
    Parse the mfapi JSON response into a DataFrame and save to data/raw/.

    mfapi JSON structure:
    {
      "meta": { "scheme_name": ..., "scheme_code": ..., ... },
      "data": [ {"date": "DD-MM-YYYY", "nav": "123.45"}, ... ],
      "status": "SUCCESS"
    }
    """
    if data is None:
        print(f"    [SKIP] No data to parse for {scheme_name}.")
        return None

    if data.get("status") != "SUCCESS":
        print(f"    [WARN] API status not SUCCESS: {data.get('status')}")

    nav_records = data.get("data", [])
    meta        = data.get("meta", {})

    if not nav_records:
        print(f"    [WARN] Empty NAV history for {scheme_name}.")
        return None

    df = pd.DataFrame(nav_records)
    df.rename(columns={"date": "nav_date", "nav": "nav_value"}, inplace=True)

    # Parse dates and cast NAV to float
    df["nav_date"]    = pd.to_datetime(df["nav_date"], format="%d-%m-%Y", errors="coerce")
    df["nav_value"]   = pd.to_numeric(df["nav_value"], errors="coerce")

    # Attach metadata columns
    df["scheme_code"] = scheme_code
    df["scheme_name"] = meta.get("scheme_name", scheme_name)
    df["fund_house"]  = meta.get("fund_house", "")
    df["scheme_type"] = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")
    df["fetched_at"]  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sort newest first
    df.sort_values("nav_date", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Save CSV
    safe_name = scheme_name.lower().replace(" ", "_").replace("/", "_")
    out_path  = os.path.join(RAW_DIR, f"nav_{scheme_code}_{safe_name}.csv")
    df.to_csv(out_path, index=False)

    print(f"    ✓ Saved  : {os.path.basename(out_path)}")
    print(f"      Rows   : {len(df):,}")
    print(f"      Period : {df['nav_date'].min().date()} → {df['nav_date'].max().date()}")
    print(f"      Latest NAV: ₹ {df['nav_value'].iloc[0]:.4f}  "
          f"({df['nav_date'].iloc[0].date()})")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Task 4: Fetch HDFC Top 100 Direct
# ─────────────────────────────────────────────────────────────────────────────

def task4_fetch_hdfc() -> pd.DataFrame | None:
    section(f"TASK 4 — Fetching HDFC Top 100 Direct (code: {HDFC_TOP_100['scheme_code']})")
    code = HDFC_TOP_100["scheme_code"]
    name = HDFC_TOP_100["scheme_name"]
    print(f"  GET https://api.mfapi.in/mf/{code}")
    data = fetch_nav(code)
    return parse_and_save(data, name, code)


# ─────────────────────────────────────────────────────────────────────────────
# Task 5: Fetch 5 key schemes
# ─────────────────────────────────────────────────────────────────────────────

def task5_fetch_key_schemes() -> list[pd.DataFrame]:
    section("TASK 5 — Fetching 5 Key Large-Cap Schemes")
    results = []
    for scheme in KEY_SCHEMES:
        code = scheme["scheme_code"]
        name = scheme["scheme_name"]
        print(f"\n  [{code}] {name}")
        print(f"  GET https://api.mfapi.in/mf/{code}")
        data = fetch_nav(code)
        df   = parse_and_save(data, name, code)
        if df is not None:
            results.append(df)
        time.sleep(0.5)   # polite delay between API calls
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Combine all fetched NAV data into one master file
# ─────────────────────────────────────────────────────────────────────────────

def combine_and_save(all_dfs: list[pd.DataFrame]) -> None:
    section("COMBINING ALL FETCHED NAV DATA")
    if not all_dfs:
        print("  [SKIP] No DataFrames to combine.")
        return

    combined = pd.concat(all_dfs, ignore_index=True)
    out_path = os.path.join(RAW_DIR, "live_nav_all_schemes.csv")
    combined.to_csv(out_path, index=False)

    print(f"  ✓ Combined file : {out_path}")
    print(f"    Total rows    : {len(combined):,}")
    print(f"    Schemes       : {combined['scheme_code'].nunique()}")
    print(f"    Date range    : {combined['nav_date'].min().date()} "
          f"→ {combined['nav_date'].max().date()}")

    # Quick pivot: latest NAV per scheme
    latest = (
        combined
        .sort_values("nav_date", ascending=False)
        .groupby("scheme_code")
        .first()
        .reset_index()[["scheme_code", "scheme_name", "nav_date", "nav_value"]]
    )
    print("\n  Latest NAV snapshot:")
    print(latest.to_string(index=False))


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print(SEPARATOR)
    print("  Capstone Project I — Mutual Fund Analytics")
    print("  Day 1: Live NAV Fetch (mfapi.in)")
    print(SEPARATOR)

    all_dfs = []

    # Task 4
    hdfc_df = task4_fetch_hdfc()
    if hdfc_df is not None:
        all_dfs.append(hdfc_df)

    # Task 5
    scheme_dfs = task5_fetch_key_schemes()
    all_dfs.extend(scheme_dfs)

    # Combine
    combine_and_save(all_dfs)

    section("LIVE NAV FETCH COMPLETE ✓")
    print(f"  Raw CSVs saved to: {RAW_DIR}")
    print(f"  Next step: Run data_ingestion.py to load & validate all datasets.")
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    main()
