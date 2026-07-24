# Capstone Project I — Mutual Fund Analytics
**Bluestock Fintech | N100 Financial Intelligence Platform**

---

## 📁 Project Structure

```
CapstoneProject/
├── data/
│   ├── raw/            ← Source CSVs & live NAV fetches
│   └── processed/      ← Cleaned, transformed datasets
├── notebooks/          ← Jupyter notebooks for EDA & analysis
├── sql/                ← SQL scripts for DB operations
├── dashboard/          ← Dashboard assets & Plotly exports
├── reports/            ← Generated reports (Markdown, PDF)
├── data_ingestion.py   ← Day 1: Load & validate all 10 CSVs
├── live_nav_fetch.py   ← Day 1: Fetch live NAV from mfapi.in
├── requirements.txt    ← Python dependencies
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place your 10 CSV datasets in data/raw/

# 3. Fetch live NAV data (internet required)
python live_nav_fetch.py

# 4. Run data ingestion & validation
python data_ingestion.py
```

---

## 📦 Dependencies
See [requirements.txt](./requirements.txt)

---

## 📅 Progress

| Day | Topic                        | Status      |
|-----|------------------------------|-------------|
| 1   | Project Setup + ETL          | ✅ Complete  |
| 2   | SQL & Database Layer         | 🔲 Pending  |
| 3   | Returns & Risk Analytics     | 🔲 Pending  |
| 4   | Dashboard                    | 🔲 Pending  |
| 5   | Report & Submission          | 🔲 Pending  |

---

## 🔗 Data Sources
- **mfapi.in** — Free mutual fund NAV API (no key required)
  - Base URL: `https://api.mfapi.in/mf/{scheme_code}`
- **AMFI** — Association of Mutual Funds in India
- Provided CSV datasets (fund_master, nav_history, etc.)

---

## 👤 Author
**bcb4314** | Bluestock Fintech Capstone — MJ28 Batch
