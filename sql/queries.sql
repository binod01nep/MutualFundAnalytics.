-- ============================================================
-- Capstone Project I — Mutual Fund Analytics
-- Day 2: Analytical SQL Queries
-- File: queries.sql
-- ============================================================

-- 1. Top 5 funds by AUM
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    p.aum_crore
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for HDFC Top 100 (amfi_code = 119598 or 125497, depending on what's in fact_nav)
-- Let's do it generally for top 5 funds or a specific fund
SELECT 
    d.year,
    d.month_name,
    f.scheme_name,
    ROUND(AVG(n.nav), 2) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date_id
JOIN dim_fund f ON n.amfi_code = f.amfi_code
WHERE f.amfi_code = 125497 -- Assuming HDFC Top 100
GROUP BY d.year, d.month, d.month_name, f.scheme_name
ORDER BY d.year DESC, d.month DESC
LIMIT 12;

-- 3. SIP YoY Growth
SELECT 
    d.year,
    SUM(t.amount_inr) AS total_sip_amount,
    COUNT(t.transaction_id) AS sip_transactions
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date_id
WHERE t.transaction_type = 'SIP'
GROUP BY d.year
ORDER BY d.year ASC;

-- 4. Transactions by State
SELECT 
    state,
    transaction_type,
    COUNT(transaction_id) as total_transactions,
    ROUND(SUM(amount_inr), 2) as total_amount_inr
FROM fact_transactions
GROUP BY state, transaction_type
ORDER BY total_amount_inr DESC;

-- 5. Funds with expense ratio < 1%
SELECT 
    amfi_code,
    scheme_name,
    fund_house,
    category,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Best Performing Funds over 5 years (return > 15%)
SELECT 
    f.scheme_name,
    f.category,
    p.return_5yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.return_5yr_pct > 15.0
ORDER BY p.return_5yr_pct DESC
LIMIT 10;

-- 7. High Risk Funds vs Sharpe Ratio (Risk vs Reward)
SELECT 
    f.scheme_name,
    f.risk_category,
    p.sharpe_ratio,
    p.std_dev_ann_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE f.risk_category IN ('High', 'Very High')
ORDER BY p.sharpe_ratio DESC
LIMIT 10;

-- 8. Most Popular Payment Modes for Lumpsum Investments
SELECT 
    payment_mode,
    COUNT(transaction_id) as transaction_count,
    ROUND(SUM(amount_inr), 2) as total_invested
FROM fact_transactions
WHERE transaction_type = 'Lumpsum'
GROUP BY payment_mode
ORDER BY total_invested DESC;

-- 9. AUM Concentration by Fund House
SELECT 
    f.fund_house,
    ROUND(SUM(p.aum_crore), 2) AS total_aum_crore,
    COUNT(f.amfi_code) AS total_schemes
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
GROUP BY f.fund_house
ORDER BY total_aum_crore DESC;

-- 10. Investor Demographics (Age Group & Gender) Analysis
SELECT 
    age_group,
    gender,
    COUNT(DISTINCT investor_id) as unique_investors,
    ROUND(AVG(amount_inr), 2) as avg_transaction_amount
FROM fact_transactions
GROUP BY age_group, gender
ORDER BY age_group, gender;
