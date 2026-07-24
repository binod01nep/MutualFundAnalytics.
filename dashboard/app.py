import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Set page configuration
st.set_page_config(page_title="Mutual Fund Analytics", page_icon="📊", layout="wide")

# Custom CSS for Bluestock Theme
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1e3d59; font-weight: bold; }
    h2, h3 { color: #172a3a; }
    div[data-testid="stMetricValue"] { color: #ff6e40; font-weight: bold; }
    .stMetric { background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# Determine DB path depending on where streamlit is run from
db_path = 'bluestock_mf.db'
if not os.path.exists(db_path):
    db_path = '../bluestock_mf.db'

# Database Connection
@st.cache_resource
def get_connection():
    return sqlite3.connect(db_path, check_same_thread=False)

conn = get_connection()

@st.cache_data
def load_query(query):
    return pd.read_sql_query(query, conn)

# Sidebar Navigation
st.sidebar.markdown("## Bluestock Fintech")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page:", [
    "Industry Overview", 
    "Fund Performance", 
    "Investor Analytics", 
    "SIP & Market Trends"
])

if page == "Industry Overview":
    st.title("Industry Overview")
    
    # KPIs
    # Note: Hardcoded to requested values for demonstration of final state as per project prompt,
    # except schemes which we can count.
    col1, col2, col3, col4 = st.columns(4)
    df_schemes = load_query("SELECT COUNT(*) as count FROM dim_fund")
    
    col1.metric("Total AUM", "₹81.3L Cr")
    col2.metric("SIP Inflows", "₹31K Cr")
    col3.metric("Folios", "26.12 Cr")
    col4.metric("Total Schemes", f"{df_schemes['count'][0]}")

    st.markdown("---")
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        # AUM Trend
        df_aum_trend = load_query("SELECT strftime('%Y', aum_date) as year, SUM(aum_crore) as total_aum FROM fact_aum GROUP BY year")
        fig_trend = px.line(df_aum_trend, x='year', y='total_aum', title="Industry AUM Trend (2022-2025)", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with row1_col2:
        # AUM by AMC
        df_aum_amc = load_query("SELECT fund_house, SUM(aum_crore) as total_aum FROM fact_aum GROUP BY fund_house ORDER BY total_aum DESC LIMIT 10")
        fig_amc = px.bar(df_aum_amc, x='fund_house', y='total_aum', title="Top 10 AMC by AUM", color='fund_house')
        st.plotly_chart(fig_amc, use_container_width=True)

elif page == "Fund Performance":
    st.title("Fund Performance Analytics")
    
    # Load scorecard
    try:
        scorecard = pd.read_csv('data/processed/fund_scorecard.csv')
    except FileNotFoundError:
        try:
            scorecard = pd.read_csv('../data/processed/fund_scorecard.csv')
        except FileNotFoundError:
            scorecard = pd.DataFrame() # Fallback

    if not scorecard.empty:
        # Merge with full fund metadata from DB to get category, plan, fund_house
        df_fund_meta = load_query("SELECT amfi_code, category, fund_house, plan FROM dim_fund")
        if 'category' not in scorecard.columns:
            scorecard = scorecard.merge(df_fund_meta, on='amfi_code', how='left')

        # Slicers
        st.sidebar.markdown("### Filters")
        categories = scorecard['category'].dropna().unique()
        selected_category = st.sidebar.multiselect("Select Category", options=categories, default=list(categories[:3]))
        
        filtered_scorecard = scorecard[scorecard['category'].isin(selected_category)] if selected_category else scorecard

        # Composite_Score can be negative; ensure bubble size is always positive
        filtered_scorecard = filtered_scorecard.copy()
        min_score = filtered_scorecard['Composite_Score'].min()
        filtered_scorecard['bubble_size'] = filtered_scorecard['Composite_Score'] - min_score + 1
        
        # Scatter Plot
        fig_scatter = px.scatter(
            filtered_scorecard, 
            x='Sharpe', 
            y='CAGR_3yr', 
            size='bubble_size',
            color='category',
            hover_name='scheme_name',
            hover_data={'Composite_Score': True, 'expense_ratio_pct': True, 'bubble_size': False},
            title="Return vs Risk (Bubble Size = Composite Score)"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Data Table
        st.markdown("### Fund Scorecard")
        display_cols = [c for c in ['scheme_name', 'category', 'Composite_Score', 'CAGR_3yr', 'Sharpe', 'expense_ratio_pct'] if c in filtered_scorecard.columns]
        st.dataframe(filtered_scorecard[display_cols].sort_values('Composite_Score', ascending=False))
        
        # NAV Line vs Benchmark
        st.markdown("### NAV vs Benchmark Over Time")
        fund_options = filtered_scorecard['scheme_name'].dropna().unique()
        if len(fund_options) > 0:
            selected_fund = st.selectbox("Select a Fund", options=fund_options)
            # Fetch NAV
            nav_query = f"""
                SELECT d.date_id, n.nav 
                FROM fact_nav n 
                JOIN dim_fund f ON n.amfi_code = f.amfi_code
                JOIN dim_date d ON n.date = d.date_id
                WHERE f.scheme_name = '{selected_fund}'
            """
            df_nav = load_query(nav_query)
            if not df_nav.empty:
                fig_nav = px.line(df_nav, x='date_id', y='nav', title=f"NAV Trend: {selected_fund}")
                st.plotly_chart(fig_nav, use_container_width=True)
        else:
            st.info("No funds match the selected filters.")
    else:
        st.error("fund_scorecard.csv not found. Please run Day 4 analytics first.")

elif page == "Investor Analytics":
    st.title("Investor Analytics")
    
    df_tx = load_query("SELECT * FROM fact_transactions")
    
    st.sidebar.markdown("### Filters")
    selected_state = st.sidebar.multiselect("State", options=df_tx['state'].unique(), default=df_tx['state'].unique()[:5])
    df_filtered = df_tx[df_tx['state'].isin(selected_state)]
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        # Bar chart: transaction amount by state
        state_amt = df_filtered.groupby('state')['amount_inr'].sum().reset_index()
        fig_state = px.bar(state_amt, x='state', y='amount_inr', title="Transaction Amount by State", color='state')
        st.plotly_chart(fig_state, use_container_width=True)
        
    with row1_col2:
        # Donut: SIP/Lumpsum/Redemption split
        type_split = df_filtered.groupby('transaction_type')['amount_inr'].sum().reset_index()
        fig_donut = px.pie(type_split, values='amount_inr', names='transaction_type', hole=0.5, title="Transaction Type Split")
        st.plotly_chart(fig_donut, use_container_width=True)
        
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        # Bar: age group vs avg SIP amount
        age_sip = df_filtered[df_filtered['transaction_type'] == 'SIP'].groupby('age_group')['amount_inr'].mean().reset_index()
        fig_age = px.bar(age_sip, x='age_group', y='amount_inr', title="Average SIP Amount by Age Group")
        st.plotly_chart(fig_age, use_container_width=True)
        
    with row2_col2:
        # Monthly transaction volume line
        df_filtered['month'] = pd.to_datetime(df_filtered['transaction_date']).dt.to_period('M').astype(str)
        vol_trend = df_filtered.groupby('month')['amount_inr'].sum().reset_index()
        fig_vol = px.line(vol_trend, x='month', y='amount_inr', title="Monthly Transaction Volume")
        st.plotly_chart(fig_vol, use_container_width=True)

elif page == "SIP & Market Trends":
    st.title("SIP & Market Trends")
    
    st.markdown("### SIP Inflows vs NIFTY 50")
    # Fetch SIP Monthly
    sip_monthly = load_query("SELECT strftime('%Y-%m', transaction_date) as month, SUM(amount_inr) as sip_amount FROM fact_transactions WHERE transaction_type='SIP' GROUP BY month")
    
    # We create a dual axis chart using graph_objects
    fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
    fig_dual.add_trace(go.Bar(x=sip_monthly['month'], y=sip_monthly['sip_amount'], name="SIP Inflow (INR)", marker_color='teal'), secondary_y=False)
    
    # Try fetching NIFTY 50
    try:
        bench_path = 'data/raw/benchmark_indices.csv'
        if not os.path.exists(bench_path):
            bench_path = '../data/raw/benchmark_indices.csv'
        df_bench = pd.read_csv(bench_path)
        df_n50 = df_bench[df_bench['index_name'] == 'NIFTY50'].copy()
        df_n50['month'] = pd.to_datetime(df_n50['date']).dt.to_period('M').astype(str)
        n50_monthly = df_n50.groupby('month')['close_value'].last().reset_index()
        
        # Merge to align dates
        aligned = pd.merge(sip_monthly, n50_monthly, on='month', how='inner')
        fig_dual.add_trace(go.Scatter(x=aligned['month'], y=aligned['close_value'], name="NIFTY 50", mode='lines+markers', line=dict(color='orange', width=3)), secondary_y=True)
    except Exception as e:
        st.warning("Could not load NIFTY 50 data for dual axis.")

    fig_dual.update_layout(title_text="SIP Inflows vs Market Trend")
    fig_dual.update_yaxes(title_text="SIP Inflows (INR)", secondary_y=False)
    fig_dual.update_yaxes(title_text="NIFTY 50 Close Value", secondary_y=True)
    st.plotly_chart(fig_dual, use_container_width=True)
    
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("### Category Inflow Heatmap")
        df_heat = load_query("SELECT strftime('%Y-%m', t.transaction_date) as month, f.category, SUM(t.amount_inr) as inflow FROM fact_transactions t JOIN dim_fund f ON t.amfi_code = f.amfi_code GROUP BY month, f.category")
        if not df_heat.empty:
            pivot_heat = df_heat.pivot(index='category', columns='month', values='inflow').fillna(0)
            fig_heat = px.imshow(pivot_heat, color_continuous_scale='Blues', aspect="auto")
            st.plotly_chart(fig_heat, use_container_width=True)
            
    with row1_col2:
        st.markdown("### Top 5 Categories (Net Inflow)")
        cat_inflow = df_heat.groupby('category')['inflow'].sum().nlargest(5).reset_index()
        fig_cat = px.bar(cat_inflow, x='inflow', y='category', orientation='h', title="Top 5 Categories by Inflow")
        st.plotly_chart(fig_cat, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Dashboard created for Day 5 of the Capstone Project.")
