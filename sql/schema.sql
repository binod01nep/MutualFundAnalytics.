-- ============================================================
-- Capstone Project I — Mutual Fund Analytics
-- Day 2: SQLite Star Schema Design
-- File: schema.sql
-- ============================================================

-- Drop existing tables to ensure a clean slate when running
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_fund;

-- ------------------------------------------------------------
-- 1. DIMENSION TABLES
-- ------------------------------------------------------------

-- dim_fund
-- Central dimension containing all mutual fund static details
CREATE TABLE dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date DATE,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- dim_date
-- Date dimension for robust time-series analysis
CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    month_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- ------------------------------------------------------------
-- 2. FACT TABLES
-- ------------------------------------------------------------

-- fact_nav
-- Granularity: Daily per Fund
CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    date DATE NOT NULL,
    nav REAL NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date (date_id)
);

CREATE INDEX idx_fact_nav_amfi_date ON fact_nav (amfi_code, date);

-- fact_transactions
-- Granularity: Individual Investor Transaction
CREATE TABLE fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    amfi_code INTEGER NOT NULL,
    transaction_type TEXT NOT NULL, -- SIP, Lumpsum, Redemption
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh TEXT,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date (date_id)
);

CREATE INDEX idx_fact_transactions_amfi ON fact_transactions (amfi_code);
CREATE INDEX idx_fact_transactions_date ON fact_transactions (transaction_date);

-- fact_performance
-- Granularity: Current Performance snapshot per Fund
CREATE TABLE fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);

CREATE INDEX idx_fact_perf_amfi ON fact_performance (amfi_code);

-- fact_aum
-- Granularity: AUM Snapshot (derived from aum_by_fund_house or scheme_performance)
-- Since we have aum_by_fund_house, we can record fund house level AUM or scheme level
CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    fund_house TEXT,
    aum_date DATE,
    aum_crore REAL NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);
