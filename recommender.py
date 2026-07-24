#!/usr/bin/env python
"""
Fund Recommender — Day 6 Capstone Project
Usage: python recommender.py <risk_appetite>
  risk_appetite: Low | Moderate | High

Examples:
  python recommender.py Low
  python recommender.py Moderate
  python recommender.py High
"""

import sys
import sqlite3
import pandas as pd
import numpy as np

# --- Config ---
DB_PATH = "bluestock_mf.db"
RF = 0.065  # RBI repo rate proxy

RISK_MAPPING = {
    "low":       ["Low"],
    "moderate":  ["Moderate", "Moderately High"],
    "high":      ["High", "Very High"],
}


def compute_sharpe(nav_df, amfi_code):
    """Compute annualised Sharpe for a given amfi_code."""
    nav = nav_df[nav_df["amfi_code"] == amfi_code].sort_values("date")["nav"]
    if len(nav) < 30:
        return np.nan
    returns = nav.pct_change().dropna()
    rf_daily = (1 + RF) ** (1 / 252) - 1
    excess = returns - rf_daily
    std = excess.std()
    if std == 0:
        return np.nan
    return (excess.mean() / std) * np.sqrt(252)


def recommend(risk_appetite: str):
    appetite = risk_appetite.strip().lower()
    if appetite not in RISK_MAPPING:
        print(f"ERROR: Invalid risk appetite '{risk_appetite}'. Choose from: Low, Moderate, High")
        sys.exit(1)

    categories = RISK_MAPPING[appetite]

    conn = sqlite3.connect(DB_PATH)
    df_fund = pd.read_sql_query(
        "SELECT amfi_code, scheme_name, risk_category, expense_ratio_pct FROM dim_fund",
        conn
    )
    df_nav = pd.read_sql_query(
        "SELECT amfi_code, date, nav FROM fact_nav ORDER BY date",
        conn
    )
    conn.close()

    # Filter funds by risk category
    eligible = df_fund[df_fund["risk_category"].isin(categories)].copy()
    if eligible.empty:
        print(f"No funds found for risk category: {categories}")
        return

    # Compute Sharpe for each eligible fund
    eligible["Sharpe"] = eligible["amfi_code"].apply(lambda c: compute_sharpe(df_nav, c))
    eligible = eligible.dropna(subset=["Sharpe"]).sort_values("Sharpe", ascending=False)

    top3 = eligible[["scheme_name", "risk_category", "Sharpe", "expense_ratio_pct"]].head(3)
    top3.columns = ["Scheme Name", "Risk Category", "Sharpe Ratio", "Expense Ratio (%)"]
    top3 = top3.reset_index(drop=True)
    top3.index += 1  # Rank starts at 1

    print(f"\n{'='*65}")
    print(f"  Fund Recommendations — Risk Appetite: {risk_appetite.capitalize()}")
    print(f"  Matching Risk Categories: {', '.join(categories)}")
    print(f"{'='*65}")
    print(top3.to_string())
    print(f"{'='*65}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    recommend(sys.argv[1])
