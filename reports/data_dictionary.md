# Data Dictionary

This document details the schema and business definitions for the `bluestock_mf.db` analytical star schema database.

## 1. Dimension Tables

### `dim_fund`
Stores static information about each mutual fund scheme.
- `amfi_code` (INTEGER, Primary Key): Unique identifier assigned by AMFI.
- `fund_house` (TEXT): The Asset Management Company (AMC) managing the fund.
- `scheme_name` (TEXT): The full name of the mutual fund scheme.
- `category` (TEXT): The broad category of the fund (e.g., Equity, Debt).
- `sub_category` (TEXT): More specific classification (e.g., Large Cap, Liquid).
- `plan` (TEXT): Direct or Regular plan.
- `launch_date` (DATE): When the fund was launched.
- `benchmark` (TEXT): The benchmark index against which performance is measured.
- `expense_ratio_pct` (REAL): Annual fee charged by the AMC, represented as a percentage.
- `exit_load_pct` (REAL): Fee charged if units are redeemed within a specific period.
- `min_sip_amount` (INTEGER): Minimum amount required for a Systematic Investment Plan.
- `min_lumpsum_amount` (INTEGER): Minimum amount for a one-time lumpsum investment.
- `fund_manager` (TEXT): The primary person managing the fund's portfolio.
- `risk_category` (TEXT): The risk profile of the fund (e.g., Moderate, Very High).
- `sebi_category_code` (TEXT): Regulatory category code.

### `dim_date`
Generated date dimension to support time-series queries.
- `date_id` (DATE, Primary Key): ISO formatted date (YYYY-MM-DD).
- `year` (INTEGER): The year.
- `month` (INTEGER): The month (1-12).
- `day` (INTEGER): The day of the month (1-31).
- `quarter` (INTEGER): The calendar quarter (1-4).
- `day_of_week` (INTEGER): Day of the week (e.g., Monday = 0, Sunday = 6).
- `day_name` (TEXT): Name of the day (e.g., 'Monday').
- `month_name` (TEXT): Name of the month (e.g., 'January').
- `is_weekend` (BOOLEAN): True if Saturday or Sunday, False otherwise.

## 2. Fact Tables

### `fact_nav`
Stores the daily Net Asset Value (NAV) for the funds.
- `nav_id` (INTEGER, Primary Key): Surrogate key.
- `amfi_code` (INTEGER, Foreign Key to `dim_fund`): The fund identifier.
- `date` (DATE, Foreign Key to `dim_date`): The date of the NAV.
- `nav` (REAL): The Net Asset Value per unit on that date.

### `fact_transactions`
Records individual investor transactions.
- `transaction_id` (INTEGER, Primary Key): Surrogate key.
- `investor_id` (TEXT): Masked unique identifier for the investor.
- `transaction_date` (DATE, Foreign Key to `dim_date`): When the transaction occurred.
- `amfi_code` (INTEGER, Foreign Key to `dim_fund`): The fund being transacted.
- `transaction_type` (TEXT): The type of transaction (SIP, Lumpsum, Redemption).
- `amount_inr` (REAL): The transaction amount in Indian Rupees.
- `state` (TEXT): State where the investor resides.
- `city` (TEXT): City where the investor resides.
- `city_tier` (TEXT): Tier classification of the city (Tier 1, Tier 2, etc.).
- `age_group` (TEXT): Age bracket of the investor.
- `gender` (TEXT): Gender of the investor.
- `annual_income_lakh` (TEXT): Income bracket in Lakhs INR.
- `payment_mode` (TEXT): Method of payment (e.g., UPI, NetBanking).
- `kyc_status` (TEXT): KYC verification status.

### `fact_performance`
Snapshot of the latest performance metrics for each fund.
- `performance_id` (INTEGER, Primary Key): Surrogate key.
- `amfi_code` (INTEGER, Foreign Key to `dim_fund`): The fund identifier.
- `return_1yr_pct` (REAL): 1-year trailing return percentage.
- `return_3yr_pct` (REAL): 3-year annualized return percentage.
- `return_5yr_pct` (REAL): 5-year annualized return percentage.
- `benchmark_3yr_pct` (REAL): 3-year return of the fund's benchmark index.
- `alpha` (REAL): Measure of the fund's excess return over the benchmark.
- `beta` (REAL): Measure of the fund's volatility relative to the market.
- `sharpe_ratio` (REAL): Risk-adjusted return metric.
- `sortino_ratio` (REAL): Risk-adjusted return metric focusing on downside deviation.
- `std_dev_ann_pct` (REAL): Annualized standard deviation of returns.
- `max_drawdown_pct` (REAL): Maximum observed loss from a peak.
- `aum_crore` (REAL): Assets Under Management in Crores INR.
- `expense_ratio_pct` (REAL): Annual fee percentage.
- `morningstar_rating` (INTEGER): Rating out of 5 stars.
- `risk_grade` (TEXT): Risk assessment grade.

### `fact_aum`
Tracks historical or current AUM data at the fund house or scheme level.
- `aum_id` (INTEGER, Primary Key): Surrogate key.
- `amfi_code` (INTEGER, Foreign Key to `dim_fund`): Nullable if tracked at fund house level.
- `fund_house` (TEXT): The Asset Management Company.
- `aum_date` (DATE): The date of the snapshot.
- `aum_crore` (REAL): Total Assets Under Management in Crores INR.
