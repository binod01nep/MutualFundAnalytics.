"""
============================================================
Capstone Project I — Mutual Fund Analytics
Day 1: Data Ingestion (ETL)
File   : data_ingestion.py
Author : bcb4314
Purpose: Load, inspect, and validate all 10 CSV datasets.
         Explore fund_master and validate AMFI codes against
         nav_history. Write a data quality summary.
============================================================
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
RAW_DIR        = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR  = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR    = os.path.join(BASE_DIR, "reports")

os.makedirs(RAW_DIR,       exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR,   exist_ok=True)

# ── Expected CSV datasets ─────────────────────────────────────────────────────
# Update these filenames to match the actual files in data/raw/
EXPECTED_DATASETS = [
    "fund_master.csv",
    "nav_history.csv",
    "portfolio_holdings.csv",
    "returns_data.csv",
    "benchmark_data.csv",
    "scheme_details.csv",
    "aum_data.csv",
    "risk_metrics.csv",
    "expense_ratio.csv",
    "investor_data.csv",
]

SEPARATOR = "=" * 70


# ─────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def inspect_dataframe(name: str, df: pd.DataFrame) -> dict:
    """
    Print shape, dtypes, head, and basic anomalies for a dataframe.
    Returns a summary dict for the quality report.
    """
    print(f"\n{'─'*60}")
    print(f"  Dataset : {name}")
    print(f"{'─'*60}")
    print(f"  Shape   : {df.shape[0]:,} rows × {df.shape[1]} columns")

    # ── Dtypes ───────────────────────────────────────────────────────────────
    print("\n  Column dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"    {col:<35} {str(dtype)}")

    # ── Head ─────────────────────────────────────────────────────────────────
    print("\n  First 3 rows:")
    print(df.head(3).to_string(index=False))

    # ── Anomaly detection ─────────────────────────────────────────────────────
    null_counts  = df.isnull().sum()
    dup_count    = df.duplicated().sum()
    anomalies    = []

    if null_counts.any():
        cols_with_nulls = null_counts[null_counts > 0]
        anomalies.append(f"Nulls in: {dict(cols_with_nulls)}")

    if dup_count > 0:
        anomalies.append(f"Duplicate rows: {dup_count}")

    if anomalies:
        print("\n  ⚠ Anomalies detected:")
        for a in anomalies:
            print(f"    - {a}")
    else:
        print("\n  ✓ No anomalies detected.")

    return {
        "dataset"   : name,
        "rows"      : df.shape[0],
        "columns"   : df.shape[1],
        "nulls"     : int(null_counts.sum()),
        "duplicates": int(dup_count),
        "anomalies" : "; ".join(anomalies) if anomalies else "None",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Task 3: Load all CSV datasets
# ─────────────────────────────────────────────────────────────────────────────

def load_all_datasets() -> dict[str, pd.DataFrame]:
    """
    Load all expected CSV files from data/raw/.
    Prints shape, dtypes, head and anomaly notes for each.
    Returns a dict: { filename_stem: DataFrame }.
    """
    section("TASK 3 — Loading All CSV Datasets")

    dataframes   = {}
    quality_rows = []
    missing      = []

    for filename in EXPECTED_DATASETS:
        filepath = os.path.join(RAW_DIR, filename)
        stem     = os.path.splitext(filename)[0]

        if not os.path.exists(filepath):
            print(f"\n  [SKIP] {filename} — file not found in data/raw/")
            missing.append(filename)
            continue

        try:
            df = pd.read_csv(filepath, low_memory=False)
            dataframes[stem] = df
            summary = inspect_dataframe(filename, df)
            quality_rows.append(summary)
        except Exception as exc:
            print(f"\n  [ERROR] Could not load {filename}: {exc}")
            missing.append(filename)

    if missing:
        print(f"\n  ⚠ Missing files ({len(missing)}):")
        for m in missing:
            print(f"    - {m}")

    return dataframes, quality_rows


# ─────────────────────────────────────────────────────────────────────────────
# Task 6: Explore fund_master
# ─────────────────────────────────────────────────────────────────────────────

def explore_fund_master(df: pd.DataFrame) -> None:
    """
    Print unique fund houses, categories, sub-categories,
    risk grades and explain AMFI scheme code structure.
    """
    section("TASK 6 — Exploring Fund Master")

    # Possible column name variants
    col_map = {
        "fund_house"   : ["fund_house", "amc", "amc_name", "fund_name",   "amcname"],
        "category"     : ["category",   "scheme_category", "fund_category"],
        "sub_category" : ["sub_category", "subcategory", "sub_cat", "scheme_sub_category"],
        "risk_grade"   : ["risk_grade", "risk", "risk_level", "riskometer"],
        "amfi_code"    : ["amfi_code", "scheme_code", "schemeCode", "amfi"],
    }

    def find_col(df, candidates):
        for c in candidates:
            if c in df.columns:
                return c
            # case-insensitive fallback
            for col in df.columns:
                if col.lower() == c.lower():
                    return col
        return None

    def print_unique(label, col):
        if col:
            vals = df[col].dropna().unique()
            print(f"\n  {label} (col='{col}') — {len(vals)} unique:")
            for v in sorted(vals):
                print(f"    • {v}")
        else:
            print(f"\n  [SKIP] '{label}' column not found.")

    fh_col   = find_col(df, col_map["fund_house"])
    cat_col  = find_col(df, col_map["category"])
    sub_col  = find_col(df, col_map["sub_category"])
    risk_col = find_col(df, col_map["risk_grade"])
    code_col = find_col(df, col_map["amfi_code"])

    print_unique("Fund Houses",    fh_col)
    print_unique("Categories",     cat_col)
    print_unique("Sub-Categories", sub_col)
    print_unique("Risk Grades",    risk_col)

    # AMFI code structure
    print("\n  AMFI Scheme Code Structure:")
    print("    • AMFI (Association of Mutual Funds in India) assigns a")
    print("      unique numeric Scheme Code to every mutual fund plan.")
    print("    • Format  : 6-digit integer (e.g., 119551, 120503)")
    print("    • Encoding: [AMC prefix][Plan ID][Option suffix]")
    print("    • Used in : AMFI website, MFI API, BSE/NSE order routing.")
    if code_col:
        sample = df[code_col].dropna().head(5).tolist()
        print(f"    • Sample codes from dataset: {sample}")


# ─────────────────────────────────────────────────────────────────────────────
# Task 7: Validate AMFI codes
# ─────────────────────────────────────────────────────────────────────────────

def validate_amfi_codes(fund_master: pd.DataFrame,
                         nav_history: pd.DataFrame,
                         quality_rows: list) -> None:
    """
    Confirm every AMFI code in fund_master exists in nav_history.
    Append findings to quality_rows and write the full quality report.
    """
    section("TASK 7 — AMFI Code Validation")

    # Detect column names
    fm_code_col  = None
    nav_code_col = None

    for col in fund_master.columns:
        if "code" in col.lower() or "amfi" in col.lower() or "scheme" in col.lower():
            fm_code_col = col
            break

    for col in nav_history.columns:
        if "code" in col.lower() or "amfi" in col.lower() or "scheme" in col.lower():
            nav_code_col = col
            break

    if not fm_code_col or not nav_code_col:
        print(f"\n  [SKIP] Could not auto-detect AMFI code columns.")
        print(f"    fund_master  columns : {list(fund_master.columns)}")
        print(f"    nav_history  columns : {list(nav_history.columns)}")
        write_quality_report(quality_rows)
        return

    print(f"\n  Using columns → fund_master['{fm_code_col}'] vs nav_history['{nav_code_col}']")

    fm_codes  = set(fund_master[fm_code_col].dropna().astype(str))
    nav_codes = set(nav_history[nav_code_col].dropna().astype(str))

    missing_in_nav  = fm_codes - nav_codes
    extra_in_nav    = nav_codes - fm_codes
    matched         = fm_codes & nav_codes
    match_pct       = len(matched) / len(fm_codes) * 100 if fm_codes else 0

    print(f"\n  Results:")
    print(f"    Total codes in fund_master    : {len(fm_codes):>6,}")
    print(f"    Total codes in nav_history    : {len(nav_codes):>6,}")
    print(f"    Matched codes                 : {len(matched):>6,}  ({match_pct:.1f}%)")
    print(f"    Codes in master NOT in history: {len(missing_in_nav):>6,}")
    print(f"    Codes in history NOT in master: {len(extra_in_nav):>6,}")

    if missing_in_nav:
        sample = sorted(missing_in_nav)[:10]
        print(f"\n  ⚠ Sample missing codes (first 10): {sample}")
    else:
        print("\n  ✓ All fund_master AMFI codes found in nav_history.")

    # Append validation result to quality rows
    quality_rows.append({
        "dataset"   : "AMFI Code Validation",
        "rows"      : len(fm_codes),
        "columns"   : 2,
        "nulls"     : 0,
        "duplicates": 0,
        "anomalies" : f"Missing in nav_history: {len(missing_in_nav)}; "
                      f"Match rate: {match_pct:.1f}%",
    })

    write_quality_report(quality_rows)


# ─────────────────────────────────────────────────────────────────────────────
# Write data quality summary report
# ─────────────────────────────────────────────────────────────────────────────

def write_quality_report(quality_rows: list) -> None:
    """Write a markdown data-quality summary to reports/data_quality_summary.md."""
    section("WRITING DATA QUALITY REPORT")

    report_path = os.path.join(REPORTS_DIR, "data_quality_summary.md")
    lines = [
        "# Data Quality Summary — Day 1\n",
        f"**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
        "| Dataset | Rows | Columns | Nulls | Duplicates | Anomalies |\n",
        "|---------|------|---------|-------|------------|-----------|\n",
    ]
    for row in quality_rows:
        lines.append(
            f"| {row['dataset']} | {row['rows']:,} | {row['columns']} "
            f"| {row['nulls']} | {row['duplicates']} | {row['anomalies']} |\n"
        )

    lines += [
        "\n## Notes\n",
        "- All raw CSV files were loaded from `data/raw/`.\n",
        "- Null counts include all columns per dataset.\n",
        "- AMFI code validation checks referential integrity between "
          "`fund_master` and `nav_history`.\n",
    ]

    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n  ✓ Report saved → {report_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print(SEPARATOR)
    print("  Capstone Project I — Mutual Fund Analytics")
    print("  Day 1: Data Ingestion & Validation")
    print(SEPARATOR)

    # Task 3: Load all datasets
    dataframes, quality_rows = load_all_datasets()

    # Task 6: Explore fund_master
    if "fund_master" in dataframes:
        explore_fund_master(dataframes["fund_master"])
    else:
        print("\n  [SKIP] fund_master.csv not available — skipping exploration.")

    # Task 7: Validate AMFI codes
    if "fund_master" in dataframes and "nav_history" in dataframes:
        validate_amfi_codes(
            dataframes["fund_master"],
            dataframes["nav_history"],
            quality_rows,
        )
    else:
        print("\n  [SKIP] fund_master or nav_history not available — "
              "skipping AMFI validation.")
        write_quality_report(quality_rows)

    section("DAY 1 DATA INGESTION COMPLETE ✓")
    print("  Next step: Run live_nav_fetch.py to pull live NAV data.")
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    main()
