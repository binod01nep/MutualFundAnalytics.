import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# --- Configuration ---
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
DB_PATH = "bluestock_mf.db"
SCHEMA_PATH = "sql/schema.sql"

os.makedirs(PROCESSED_DIR, exist_ok=True)

def clean_nav_history():
    print("Cleaning nav_history.csv...")
    try:
        df = pd.read_csv(f"{RAW_DIR}/nav_history.csv")
    except FileNotFoundError:
        print("nav_history.csv not found.")
        return None
    
    # parse dates to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # sort by amfi_code + date
    df = df.sort_values(by=['amfi_code', 'date'])
    
    # forward-fill missing NAV for holidays/weekends
    # Create a complete date range per amfi_code
    def fill_nav(group):
        group = group.set_index('date')
        full_idx = pd.date_range(start=group.index.min(), end=group.index.max(), freq='D')
        group = group.reindex(full_idx)
        group['amfi_code'] = group['amfi_code'].ffill()
        group['nav'] = group['nav'].ffill()
        return group.reset_index().rename(columns={'index': 'date'})

    df = df.groupby('amfi_code').apply(fill_nav).reset_index(drop=True)
    
    # remove duplicates
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    
    # validate NAV > 0
    df = df[df['nav'] > 0]
    
    # formatting back to string for consistency
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    df.to_csv(f"{PROCESSED_DIR}/nav_history.csv", index=False)
    return df

def clean_investor_transactions():
    print("Cleaning investor_transactions.csv...")
    try:
        df = pd.read_csv(f"{RAW_DIR}/investor_transactions.csv")
    except FileNotFoundError:
        print("investor_transactions.csv not found.")
        return None
        
    # standardise transaction_type values
    type_mapping = {
        'sip': 'SIP', 'SIP': 'SIP', 'Systematic Investment Plan': 'SIP',
        'lumpsum': 'Lumpsum', 'Lumpsum': 'Lumpsum', 'LUMPSUM': 'Lumpsum',
        'redemption': 'Redemption', 'Redemption': 'Redemption', 'REDEMPTION': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].map(type_mapping).fillna('Other')
    
    # validate amount > 0
    df = df[df['amount_inr'] > 0]
    
    # fix date formats
    df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')
    
    # check kyc_status enum values
    valid_kyc = ['Verified', 'Pending', 'Rejected']
    df['kyc_status'] = df['kyc_status'].apply(lambda x: x if x in valid_kyc else 'Unknown')
    
    df.to_csv(f"{PROCESSED_DIR}/investor_transactions.csv", index=False)
    return df

def clean_scheme_performance():
    print("Cleaning scheme_performance.csv...")
    try:
        df = pd.read_csv(f"{RAW_DIR}/scheme_performance.csv")
    except FileNotFoundError:
        print("scheme_performance.csv not found.")
        return None
        
    # validate all return values are numeric
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # check expense_ratio range (0.1% - 2.5%)
    # flag anomalies by dropping or clamping, here we filter them out
    df = df[(df['expense_ratio_pct'] >= 0.1) & (df['expense_ratio_pct'] <= 2.5)]
    
    df.to_csv(f"{PROCESSED_DIR}/scheme_performance.csv", index=False)
    return df

def clean_basic(file_name):
    print(f"Cleaning {file_name}...")
    try:
        df = pd.read_csv(f"{RAW_DIR}/{file_name}")
        df = df.drop_duplicates()
        df.to_csv(f"{PROCESSED_DIR}/{file_name}", index=False)
        return df
    except FileNotFoundError:
        print(f"{file_name} not found.")
        return None

def generate_dim_date(start_date, end_date):
    print("Generating dim_date...")
    dates = pd.date_range(start=start_date, end=end_date)
    df = pd.DataFrame({'date_id': dates})
    df['year'] = df['date_id'].dt.year
    df['month'] = df['date_id'].dt.month
    df['day'] = df['date_id'].dt.day
    df['quarter'] = df['date_id'].dt.quarter
    df['day_of_week'] = df['date_id'].dt.dayofweek
    df['day_name'] = df['date_id'].dt.day_name()
    df['month_name'] = df['date_id'].dt.month_name()
    df['is_weekend'] = df['date_id'].dt.dayofweek >= 5
    df['date_id'] = df['date_id'].dt.strftime('%Y-%m-%d')
    return df

def main():
    print("--- Day 2: Data Cleaning & SQL Loading ---")
    
    # 1. Clean data
    df_nav = clean_nav_history()
    df_transactions = clean_investor_transactions()
    df_performance = clean_scheme_performance()
    
    df_fund = clean_basic("fund_master.csv")
    df_portfolio = clean_basic("portfolio_holdings.csv")
    df_aum = clean_basic("aum_by_fund_house.csv")
    clean_basic("benchmark_indices.csv")
    clean_basic("category_inflows.csv")
    clean_basic("industry_folio_count.csv")
    clean_basic("monthly_sip_inflows.csv")
    
    # Generate dim_date based on transaction/nav dates
    if df_nav is not None and df_transactions is not None:
        min_date = min(df_nav['date'].min(), df_transactions['transaction_date'].min())
        max_date = max(df_nav['date'].max(), df_transactions['transaction_date'].max())
        df_date = generate_dim_date(min_date, max_date)
    else:
        df_date = generate_dim_date("2020-01-01", "2026-12-31")
    
    # 2. Setup SQLite database
    print("Setting up SQLite database...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH) # Start fresh
        
    conn = sqlite3.connect(DB_PATH)
    
    # Execute schema
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    
    # 3. Load tables
    print("Loading data into SQLite via SQLAlchemy...")
    engine = create_engine(f"sqlite:///{DB_PATH}")
    
    if df_fund is not None:
        # subset columns that are in dim_fund to avoid schema mismatch
        cols = ['amfi_code', 'fund_house', 'scheme_name', 'category', 'sub_category', 
                'plan', 'launch_date', 'benchmark', 'expense_ratio_pct', 'exit_load_pct',
                'min_sip_amount', 'min_lumpsum_amount', 'fund_manager', 'risk_category', 'sebi_category_code']
        df_fund[cols].to_sql('dim_fund', con=engine, if_exists='append', index=False)
        print(f"Loaded {len(df_fund)} rows into dim_fund")
        
    if df_date is not None:
        df_date.to_sql('dim_date', con=engine, if_exists='append', index=False)
        print(f"Loaded {len(df_date)} rows into dim_date")
        
    if df_nav is not None:
        # chunking large tables
        df_nav[['amfi_code', 'date', 'nav']].to_sql('fact_nav', con=engine, if_exists='append', index=False, chunksize=10000)
        print(f"Loaded {len(df_nav)} rows into fact_nav")
        
    if df_transactions is not None:
        df_transactions.to_sql('fact_transactions', con=engine, if_exists='append', index=False, chunksize=10000)
        print(f"Loaded {len(df_transactions)} rows into fact_transactions")
        
    if df_performance is not None:
        cols = ['amfi_code', 'return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct',
                'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct',
                'aum_crore', 'expense_ratio_pct', 'morningstar_rating', 'risk_grade']
        df_performance[cols].to_sql('fact_performance', con=engine, if_exists='append', index=False)
        print(f"Loaded {len(df_performance)} rows into fact_performance")
        
    if df_aum is not None:
        if 'amfi_code' not in df_aum.columns:
            df_aum['amfi_code'] = None
        if 'aum_date' not in df_aum.columns and 'date' in df_aum.columns:
            df_aum = df_aum.rename(columns={'date': 'aum_date'})
            
        cols = [c for c in ['amfi_code', 'fund_house', 'aum_date', 'aum_crore'] if c in df_aum.columns]
        df_aum[cols].to_sql('fact_aum', con=engine, if_exists='append', index=False)
        print(f"Loaded {len(df_aum)} rows into fact_aum")

    conn.close()
    print("--- Done ---")

if __name__ == "__main__":
    main()
