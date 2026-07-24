# Data Quality Summary — Day 1
**Generated**: 2026-07-25 01:19:29

| Dataset | Rows | Columns | Nulls | Duplicates | Anomalies |
|---------|------|---------|-------|------------|-----------|
| fund_master.csv | 40 | 15 | 0 | 0 | None |
| nav_history.csv | 46,000 | 3 | 0 | 0 | None |
| portfolio_holdings.csv | 322 | 8 | 0 | 0 | None |
| AMFI Code Validation | 40 | 2 | 0 | 0 | Missing in nav_history: 0; Match rate: 100.0% |

## Notes
- All raw CSV files were loaded from `data/raw/`.
- Null counts include all columns per dataset.
- AMFI code validation checks referential integrity between `fund_master` and `nav_history`.
