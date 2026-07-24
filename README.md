# Bluestock Fintech — Capstone Project I: Mutual Fund Analytics

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-green)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A **7-day full-stack data analytics capstone project** built for the N100 Financial Intelligence Platform at Bluestock Fintech. The project delivers end-to-end analytics on India's mutual fund industry — from raw data ingestion to an interactive web dashboard and a fund recommender engine.

---

## Project Overview

| Item | Detail |
|---|---|
| **Data Source** | 10 CSV datasets covering 40 mutual fund schemes |
| **Database** | SQLite (`bluestock_mf.db`) — Star Schema |
| **Key Metrics** | CAGR, Sharpe, Sortino, Alpha, Beta, VaR, CVaR, Max Drawdown |
| **Dashboard** | 4-page Streamlit Web App (live at `localhost:8501`) |
| **Recommender** | CLI tool for risk-appetite based fund recommendation |

---

## Folder Structure

```
CapstoneProject/
├── data/
│   ├── raw/                   # Original CSV datasets (10 files)
│   └── processed/             # Cleaned CSVs + scorecard + risk metrics
├── notebooks/
│   ├── EDA_Analysis.ipynb         # Day 3: Exploratory Data Analysis
│   ├── Performance_Analytics.ipynb # Day 4: Fund Performance Metrics
│   └── Advanced_Analytics.ipynb   # Day 6: VaR, CVaR, Cohort, HHI
├── dashboard/
│   └── app.py                 # Streamlit 4-page web application
├── sql/
│   ├── schema.sql             # SQLite Star Schema DDL
│   └── queries.sql            # 10 analytical SQL queries
├── reports/
│   ├── *.png                  # All exported chart images
│   ├── data_dictionary.md     # Schema documentation
│   ├── Final_Report.md        # 15-section written report
│   └── Bluestock_MF_Presentation.pptx  # 12-slide presentation
├── data_ingestion.py          # Day 1: Load & validate raw CSVs
├── data_cleaning.py           # Day 2: Clean + load to SQLite
├── live_nav_fetch.py          # Day 1: Live NAV API fetch
├── build_eda.py               # Day 3: EDA Notebook generator
├── build_performance_eda.py   # Day 4: Performance Notebook generator
├── build_advanced_analytics.py # Day 6: Advanced Analytics generator
├── build_presentation.py      # Day 7: Generates the .pptx
├── recommender.py             # Day 6: CLI fund recommender
├── run_pipeline.py            # Day 7: Master run-all script
├── check_db.py                # Quick DB health check
├── bluestock_mf.db            # SQLite database (generated)
└── requirements.txt           # Python dependencies
```

---

## Datasets

| File | Description | Rows |
|---|---|---|
| `fund_master.csv` | Scheme metadata, risk grade, expense ratio | 40 |
| `nav_history.csv` | Daily NAV per scheme (2020–2026) | ~64,000+ |
| `investor_transactions.csv` | SIP/Lumpsum/Redemption records | ~32,000+ |
| `scheme_performance.csv` | Pre-computed risk metrics snapshot | 40 |
| `portfolio_holdings.csv` | Stock-level equity holdings | ~500+ |
| `aum_by_fund_house.csv` | Monthly AUM by fund house | 90 |
| `benchmark_indices.csv` | NIFTY50, NIFTY100, MIDCAP150, SMALLCAP | ~1,400+ |
| `category_inflows.csv` | Monthly net inflows by category | ~400+ |
| `industry_folio_count.csv` | Industry folio count timeline | 48 |
| `monthly_sip_inflows.csv` | Aggregate monthly SIP data | 48 |

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- Git

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run

### Option A: Run the Full Pipeline (Recommended)
This runs everything from ETL to notebooks in one command:
```bash
python run_pipeline.py
```

### Option B: Run Steps Individually

**Step 1 — Data Ingestion (Validation)**
```bash
python data_ingestion.py
```

**Step 2 — Data Cleaning + Database Loading**
```bash
python data_cleaning.py
```

**Step 3 — EDA Analysis**
```bash
python build_eda.py
jupyter nbconvert --execute --inplace notebooks/EDA_Analysis.ipynb
```

**Step 4 — Performance Analytics**
```bash
python build_performance_eda.py
jupyter nbconvert --execute --inplace notebooks/Performance_Analytics.ipynb
```

**Step 5 — Advanced Analytics & Risk Metrics**
```bash
python build_advanced_analytics.py
jupyter nbconvert --execute --inplace notebooks/Advanced_Analytics.ipynb
```

---

## Launch the Dashboard

```bash
python -m streamlit run dashboard/app.py
```
Opens at **http://localhost:8501** with 4 pages:
- **Industry Overview** — KPIs, AUM trend, AMC breakdown
- **Fund Performance** — Scatter, Scorecard, NAV chart
- **Investor Analytics** — Demographics, State analysis, SIP trends
- **SIP & Market Trends** — Dual-axis NIFTY 50 overlay, Heatmaps

---

## Fund Recommender CLI

Get the top 3 fund recommendations based on risk appetite:
```bash
python recommender.py Low       # Conservative funds (best Sharpe)
python recommender.py Moderate  # Balanced risk funds
python recommender.py High      # Aggressive growth funds
```

---

## Check the Database

```bash
python check_db.py
```
Prints all table names and row counts to verify the SQLite DB is loaded.

---

## Key Deliverables

| Day | Deliverable | File |
|---|---|---|
| Day 1 | Data Ingestion Report | `data_ingestion.py` |
| Day 2 | SQLite Database | `bluestock_mf.db` |
| Day 3 | EDA Notebook (15+ charts) | `notebooks/EDA_Analysis.ipynb` |
| Day 4 | Performance Notebook + Scorecard | `notebooks/Performance_Analytics.ipynb`, `data/processed/fund_scorecard.csv` |
| Day 5 | Interactive Dashboard | `dashboard/app.py` |
| Day 6 | Advanced Analytics + Recommender | `notebooks/Advanced_Analytics.ipynb`, `recommender.py` |
| Day 7 | Final Report + Presentation | `reports/Final_Report.md`, `reports/Bluestock_MF_Presentation.pptx` |

---

## Self-Review Checklist

- [x] All 8 project objectives met
- [x] ETL pipeline runs end-to-end without errors
- [x] SQLite DB loaded with 6 tables and 100K+ rows
- [x] 15+ charts generated across 3 Jupyter notebooks
- [x] Fund Scorecard computed and exported
- [x] Streamlit Dashboard launches and all 4 pages render
- [x] Fund Recommender works for Low / Moderate / High inputs
- [x] Final Report written (15+ sections)
- [x] 12-slide Presentation generated
- [x] GitHub repo clean with `v1.0` tag

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Data | Pandas, NumPy |
| Database | SQLite + SQLAlchemy |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Notebooks | Jupyter, nbformat, nbconvert |
| Dashboard | Streamlit |
| ML / Stats | SciPy (`linregress`) |
| Presentation | python-pptx |
| Version Control | Git + GitHub |

---

*Built for Bluestock Fintech — N100 Financial Intelligence Platform | June 2026*
