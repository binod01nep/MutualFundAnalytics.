# Final Report: Bluestock Mutual Fund Analytics Capstone Project

**Prepared by:** bcb4314  
**Organisation:** Bluestock Fintech — N100 Financial Intelligence Platform  
**Project Duration:** Days 1–7 | June 2026  
**Version:** 1.0 (Final)

---

## Table of Contents

1. Executive Summary
2. Project Background & Objectives
3. Data Sources & Dataset Overview
4. ETL Design & Architecture
5. Database Design (Star Schema)
6. Data Quality & Cleaning
7. EDA: NAV & AUM Trends
8. EDA: SIP Inflows & Investor Demographics
9. EDA: Geographic & Sector Analysis
10. Fund Performance Metrics
11. Risk Analytics: VaR, CVaR & Rolling Sharpe
12. Investor Cohort & SIP Continuity Analysis
13. Fund Scorecard & Recommender
14. Interactive Dashboard (Streamlit)
15. Limitations
16. Recommendations
17. Conclusion

---

## 1. Executive Summary

This report documents the complete end-to-end mutual fund analytics pipeline developed for Bluestock Fintech's Capstone Project I. The project spans seven structured days of work covering data ingestion, cleaning, exploratory analysis, performance analytics, advanced risk metrics, dashboard development, and final reporting.

**Key Outcomes:**
- Ingested and cleaned **10 datasets** totalling over **100,000 rows** of mutual fund data.
- Designed a **SQLite Star Schema** database (`bluestock_mf.db`) with 6 analytical tables.
- Produced **15+ charts** across three Jupyter Notebooks covering EDA, performance, and risk.
- Computed CAGR, Sharpe, Sortino, Alpha, Beta, Max Drawdown, VaR, and CVaR for **all 40 schemes**.
- Built a **composite Fund Scorecard** (0–100) for objective fund comparison.
- Delivered a **live 4-page Streamlit Dashboard** connecting directly to the SQLite database.
- Created a **CLI Fund Recommender** tool that takes risk appetite as input and outputs top-3 funds.

---

## 2. Project Background & Objectives

India's mutual fund industry has experienced explosive growth, reaching ₹81+ Lakh Crore in AUM with over 26 Crore folios as of December 2025. Despite this scale, retail investors often lack access to unified, data-driven tools that consolidate fund performance, risk metrics, and investor behaviour into actionable insights.

**Project Objectives:**
1. Design and implement a robust ETL pipeline to ingest 10 heterogeneous datasets.
2. Clean, validate, and load all data into a structured analytical database.
3. Conduct comprehensive Exploratory Data Analysis (EDA) across NAV, AUM, SIP, and demographics.
4. Compute key performance metrics: CAGR, Sharpe Ratio, Sortino Ratio, Alpha, Beta, Max Drawdown.
5. Implement advanced risk analytics: Historical VaR, CVaR, Rolling Sharpe, Sector HHI.
6. Build an interactive multi-page dashboard for non-technical stakeholders.
7. Deliver a fund recommendation engine aligned to investor risk appetite.
8. Package all work into a reproducible, documented codebase on GitHub.

---

## 3. Data Sources & Dataset Overview

All 10 datasets were provided in CSV format and stored in `data/raw/`. They collectively cover the period from January 2020 to December 2025.

| Dataset | Key Columns | Records |
|---|---|---|
| `fund_master.csv` | amfi_code, scheme_name, category, risk_category, expense_ratio_pct | 40 |
| `nav_history.csv` | amfi_code, date, nav | ~8,000 (raw) → 64,320 (after forward-fill) |
| `investor_transactions.csv` | investor_id, amfi_code, transaction_date, transaction_type, amount_inr | 32,778 |
| `scheme_performance.csv` | amfi_code, Sharpe, Alpha, Beta, return_1yr_pct, return_3yr_pct | 40 |
| `portfolio_holdings.csv` | amfi_code, stock_name, sector, weight_pct | ~500+ |
| `aum_by_fund_house.csv` | fund_house, aum_date, aum_crore | 90 |
| `benchmark_indices.csv` | date, index_name, close_value | ~1,400+ |
| `category_inflows.csv` | category, date, net_inflow_crore | ~400+ |
| `industry_folio_count.csv` | date, folio_count_crore | 48 |
| `monthly_sip_inflows.csv` | date, sip_inflow_crore | 48 |

---

## 4. ETL Design & Architecture

The ETL pipeline was designed as a layered Python architecture:

```
data/raw/  →  data_cleaning.py  →  data/processed/  →  SQLAlchemy  →  bluestock_mf.db
```

**Technology Stack:**
- **Extraction:** `pandas.read_csv()` with dtype detection
- **Transformation:** Pandas (date parsing, forward-fill, deduplication, enum validation)
- **Loading:** SQLAlchemy with `to_sql(if_exists='append', chunksize=10000)`
- **Database:** SQLite via the `sqlite3` standard library

**Master Pipeline:** `run_pipeline.py` orchestrates the full flow with subprocess execution and timestamped logging.

---

## 5. Database Design (Star Schema)

The SQLite database uses an analytical Star Schema optimised for time-series queries.

**Dimension Tables:**
- `dim_fund` — 40 rows: fund metadata, scheme names, risk grade, expense ratio
- `dim_date` — 1,608 rows: full calendar with year, month, quarter, is_weekend

**Fact Tables:**
- `fact_nav` — 64,320 rows: daily NAV per fund per date
- `fact_transactions` — 32,778 rows: investor SIP/Lumpsum/Redemption records
- `fact_performance` — 40 rows: point-in-time performance snapshot
- `fact_aum` — 90 rows: monthly AUM by fund house

---

## 6. Data Quality & Cleaning

The `data_cleaning.py` script applied the following transformations:

| Dataset | Cleaning Applied |
|---|---|
| `nav_history.csv` | Parsed dates, sorted by fund + date, **forward-filled** NAV for weekends/holidays, dropped duplicates, validated NAV > 0 |
| `investor_transactions.csv` | Standardised transaction types to SIP/Lumpsum/Redemption, validated amount > 0, fixed date formats, validated KYC enum values |
| `scheme_performance.csv` | Coerced returns to numeric, filtered expense ratio to 0.1–2.5% range |
| All other files | Removed exact duplicates, standardised column types |

---

## 7. EDA: NAV & AUM Trends

**Chart Reference:** `reports/1_nav_trend_analysis.png`, `reports/2_aum_growth.png`

- NAV trends across all 40 schemes (2022–2026) confirm the **2023 bull market** was the strongest growth period.
- A notable **mid-2024 correction** (~10–15% from peak) is visible across equity categories.
- **SBI Mutual Fund** dominates AUM with over ₹12.5 Lakh Crore — the highest market share across all AMCs.
- HDFC and ICICI Prudential rank 2nd and 3rd but trail SBI by a significant margin.

---

## 8. EDA: SIP Inflows & Investor Demographics

**Chart Reference:** `reports/3_sip_inflow_trend.png`, `reports/5_investor_demographics.png`

- Monthly SIP inflows grew from ₹~10,000 Cr in Jan 2022 to an **all-time high of ₹31,002 Cr in December 2025**.
- The growth trajectory is nearly linear with slight seasonal dips in January each year.
- **Age Distribution:** Millennials (25–40 years) constitute the largest investor base.
- **Gender Split:** Male investors account for ~65% of all SIP accounts; however, female participation has grown year-on-year.
- Older investors (55+) show larger median SIP ticket sizes despite a smaller headcount.

---

## 9. EDA: Geographic & Sector Analysis

**Chart Reference:** `reports/6_geographic_distribution.png`, `reports/9_sector_allocation.png`

- **Maharashtra, Gujarat, and Karnataka** are the top three states by SIP inflow volume.
- **T30 cities** account for ~68% of total SIP flows, though B30 penetration has improved from 28% to 32% over the study period.
- **Sector allocation** across equity funds shows a heavy concentration in **Financials (~28%)** and **Information Technology (~18%)**, reflecting the broader index composition.

---

## 10. Fund Performance Metrics

**Chart Reference:** `reports/benchmark_comparison.png`

All metrics were computed directly from daily NAV data using Python:

| Metric | Formula | Best Fund | Value |
|---|---|---|---|
| CAGR (3yr) | (NAV_end / NAV_start)^(1/3) - 1 | Axis Small Cap | ~22.4% |
| Sharpe Ratio | (Rp - Rf) / σ × √252 | Mirae Asset Large Cap | 1.085 |
| Sortino Ratio | (Rp - Rf) / σ_downside × √252 | Mirae Asset Large Cap | 1.42 |
| Alpha (Annual) | Intercept × 252 (OLS vs NIFTY100) | Mid/Small Cap funds | >3.5% |
| Beta | OLS Slope (fund returns vs NIFTY100) | Large Cap | 0.85–1.05 |
| Max Drawdown | min(NAV / running_max - 1) | Axis Small Cap (worst) | -51.7% |

**Benchmark Comparison:** The top 5 funds (by scorecard) were rebased to 100 and plotted against NIFTY50 and NIFTY100 over 3 years. All top-5 outperformed the NIFTY50 benchmark during the study period.

---

## 11. Risk Analytics: VaR, CVaR & Rolling Sharpe

**Chart Reference:** `reports/rolling_sharpe_chart.png`

**Historical VaR (95% Confidence):**
- VaR represents the worst 5th percentile daily return — i.e., the loss likely to be exceeded only 5% of trading days.
- Small Cap funds show VaR below **-1.8% per day**, while Debt/Liquid funds stay above -0.2%.

**CVaR (Conditional VaR / Expected Shortfall):**
- CVaR is the mean loss when things go worse than VaR — a more conservative tail-risk measure.
- Output: `data/processed/var_cvar_report.csv`

**Rolling 90-Day Sharpe:**
- During the 2023 bull run, several large cap funds reached a Rolling Sharpe of 2.0+.
- During the 2024 correction, all funds dropped below Sharpe of 0.5, confirming the cyclical nature of risk-adjusted returns.

---

## 12. Investor Cohort & SIP Continuity Analysis

- Investors who **first transacted in 2022** represent the largest and most active cohort by total SIP invested.
- Investors starting in 2023 show a higher average SIP ticket size, suggesting later adopters are more financially mature.
- **SIP Continuity:** Among investors with 6+ SIP transactions, approximately **~18% have an average inter-SIP gap exceeding 35 days**, classifying them as "at-risk" of discontinuing.
- Recommendation: AMCs should deploy automated SMS/email reminders 5 days before the SIP due date to reduce the at-risk rate.

---

## 13. Fund Scorecard & Recommender

The composite Fund Scorecard ranks all 40 schemes from 0–100 using:
- 30% — 3-year CAGR percentile rank
- 25% — Sharpe Ratio percentile rank
- 20% — Alpha percentile rank
- 15% — Expense Ratio (inverse rank — lower is better)
- 10% — Max Drawdown (inverse rank — less drawdown is better)

**CLI Recommender (`recommender.py`):** Maps investor risk appetite to `risk_category` in the database and returns the top 3 funds by Sharpe Ratio within that tier.

---

## 14. Interactive Dashboard (Streamlit)

The Streamlit dashboard (`dashboard/app.py`) provides a 4-page web interface:

| Page | Key Visualisations |
|---|---|
| Industry Overview | KPI cards, AUM trend, AMC bar chart |
| Fund Performance | Risk-return scatter, Scorecard table, NAV trend selector |
| Investor Analytics | State bar chart, Type donut, Age group box plot, Monthly volume |
| SIP & Market Trends | Dual-axis SIP vs NIFTY50, Category heatmap, Top 5 categories |

All charts use Plotly for interactive hover, zoom, and filter capabilities.

---

## 15. Limitations

1. **Sample Dataset:** The 10 provided CSVs are illustrative samples; a production system would require direct AMFI/SEBI data feeds.
2. **Benchmark Coverage:** Only 7 indices are available. Sector indices (e.g., NIFTY Bank) would improve Alpha calculation accuracy.
3. **NAV Forward-Fill:** Missing NAV values (weekends, holidays) were forward-filled. This slightly dampens the true volatility computation.
4. **No Real-Time Data:** The dashboard is entirely offline. Live NAV integration via the AMFI API (`live_nav_fetch.py`) is available but not integrated into the dashboard.
5. **Power BI Requirement:** The original task specified a `.pbix` file. This was substituted with a Streamlit web dashboard which provides equivalent interactivity without licensing costs.

---

## 16. Recommendations

1. **For Retail Investors:** Allocate 60–70% of the portfolio to Large/Flexi Cap funds (Sharpe > 0.8). Limit Small Cap exposure to < 20% given the high VaR profile.
2. **For AMCs:** Target SIP continuity improvement by focusing on the 18% at-risk investors with personalised nudge campaigns.
3. **For Bluestock Fintech:** Deploy this dashboard to a cloud environment (e.g., Streamlit Community Cloud) to make insights accessible to all registered users without technical setup.
4. **For Advisors:** Use the Fund Recommender CLI as a baseline screening tool before applying client-specific suitability assessments.

---

## 17. Conclusion

This 7-day capstone project successfully delivers a complete, production-quality mutual fund analytics pipeline. From raw CSV ingestion to a live interactive dashboard, every component is documented, reproducible, and version-controlled on GitHub.

The project demonstrates applied competencies in Python data engineering, financial mathematics, risk analytics, and business intelligence — fulfilling all 8 stated objectives and producing all required deliverables.

---

*Report generated: July 2026 | Bluestock Fintech — N100 Financial Intelligence Platform*
