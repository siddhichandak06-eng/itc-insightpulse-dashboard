import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sqlalchemy as sa
import urllib.parse
from datetime import datetime, timedelta
import warnings
import numpy as np
import os
import base64
from dotenv import load_dotenv
load_dotenv() 

# ================================================================
# 🔒 SYSTEM-WIDE SECURITY LOCK Verification Check
# ================================================================
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("❌ Unauthorized Access Attempt Deflected! Please authenticate through the landing page.")
    if st.button("Return to Safety Gateway"):
        st.switch_page("app.py")
    st.stop() 

warnings.filterwarnings("ignore")

# ================================================================
# COLOR PALETTE - PROFESSIONAL BLUE THEME
# ================================================================
COLORS = {
    'primary': '#1479FF',
    'primary_light': 'rgba(20, 121, 255, 0.1)',
    'primary_medium': 'rgba(20, 121, 255, 0.3)',
    'dark_primary': '#195068',
    'dark_secondary': '#161616',
    'darker': '#003868',
    'accent1': '#14D2FF',
    'accent2': '#14EBFF',
    'accent_bright': '#00D9FF',  
    'accent_warm': '#FFB81C',    
    'white': '#FFFFFF',
    'light_bg': '#F8FBFF',
    'gray': '#94A3B8',
    'dark_gray': '#334155',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444'
}

if 'COLORS' not in st.session_state:
    st.session_state.COLORS = COLORS

# ================================================================
# CUSTOM CSS STYLING
# ================================================================
def inject_custom_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {{ font-family: 'Inter', sans-serif; }}
    html, body, [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, #000000 0%, #0a1f44 50%, #001f54 100%);
        background-attachment: fixed;
    }}
    [data-testid="stMain"] {{ background: transparent; padding-top: 2rem; }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['dark_primary']} 100%);
        border-right: 1px solid {COLORS['primary_light']};
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"], 
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] .stMarkdown {{
        color: {COLORS['white']} !important;
    }}
    h1, h1 span, .stHeadingWithAnchor h1, [data-testid="stMarkdownContainer"] h1, [data-testid="stMain"] h1 {{
        font-family: 'Times New Roman', Times, Baskerville, Georgia, serif !important;
        font-weight: 800 !important;
        font-size: 2.6rem !important;
        letter-spacing: 0.02em !important;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent2']}) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        color: transparent !important;
    }}
    h2 {{ color: {COLORS['white']} !important; font-weight: 700 !important; font-size: 1.8rem !important; }}
    h3 {{ color: {COLORS['accent1']} !important; font-weight: 600 !important; }}
    p {{ color: {COLORS['white']} !important; }}
    
    .stMetric {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 16px !important;
        border: 1px solid {COLORS['primary_medium']} !important;
        padding: 1.2rem !important;
        box-shadow: 0 20px 40px {COLORS['primary_light']};
        transition: all 0.3s ease !important;
    }}
    .stMetric:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 30px 60px {COLORS['primary_medium']};
        border-color: {COLORS['accent1']} !important;
    }}
    
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetric"] div,
    [data-testid="stMetric"] span {{
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        word-break: break-word !important;
        line-height: 1.3 !important;
    }}
    
    [data-testid="stMetricValue"] {{
        font-size: 1.35rem !important; 
        font-weight: 700 !important;
    }}
    
    .analytics-box {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        border: 1px solid {COLORS['primary_medium']} !important;
        padding: 2rem !important;
        margin: 1.5rem 0 !important;
        box-shadow: 0 20px 40px {COLORS['primary_light']};
        transition: all 0.3s ease !important;
        position: relative;
    }}
    .analytics-box::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent1']}, {COLORS['accent2']});
        border-radius: 20px 20px 0 0;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent1']}) !important;
        color: {COLORS['white']} !important;
        border: none !important; border-radius: 10px !important; padding: 12px 28px !important;
        font-weight: 600 !important; transition: all 0.3s ease !important;
    }}
    [data-testid="stSelectbox"] [role="button"], [data-testid="stMultiSelect"] [role="button"] {{
        background: rgba(20, 121, 255, 0.1) !important;
        border: 1px solid {COLORS['primary_medium']} !important;
        color: {COLORS['white']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ================================================================
# DATA LOADING & CACHING
# ================================================================
from preprocess import get_processed_data

def load_data():
    return get_processed_data()

@st.cache_data(ttl=300)
def calculate_kpis(df):
    if df.empty:
        return {col: 0 for col in ['revenue', 'units', 'transactions', 'avg_order', 'growth', 'density']}
    
    total_revenue = df['Total Amount'].sum() if 'Total Amount' in df.columns else 0
    total_transactions = len(df)
    
    return {
        'revenue': total_revenue,
        'units': df['Quantity'].sum() if 'Quantity' in df.columns else 0,
        'transactions': total_transactions,
        'avg_order': df['Total Amount'].mean() if 'Total Amount' in df.columns else 0,
        'growth': 0,  
        'density': total_revenue / total_transactions if total_transactions > 0 else 0
    }

# ================================================================
# FIXED: EXPANDED COLUMN DETECTION TO POPULATE BRAND MODULE DIAGNOSTICS
# ================================================================
def detect_columns(df):
    cols = {}
    
    date_patterns = ['Date', 'date', 'Order Date', 'order_date']
    cols['date'] = next((col for col in date_patterns if col in df.columns), 'Date')
    
    amount_patterns = ['Total Amount', 'total_amount', 'Total', 'Amount', 'Revenue']
    cols['amount'] = next((col for col in amount_patterns if col in df.columns), 'Total Amount')
    
    qty_patterns = ['Quantity', 'quantity', 'Qty', 'Units']
    cols['quantity'] = next((col for col in qty_patterns if col in df.columns), 'Quantity')
    
    cols['region'] = next((col for col in df.columns if 'Region' in col), 'Region')
    cols['brand'] = next((col for col in df.columns if 'Brand' in col), 'Brand')
    cols['distributor'] = next((col for col in df.columns if 'Distributor' in col), 'Distributor')
    
    # Structural target assignments added for sub-page calculations
    channel_patterns = ['Channel', 'channel', 'Sales Channel', 'Channels']
    cols['channel'] = next((col for col in channel_patterns if col in df.columns), 'Channel')
    
    product_patterns = ['Product Name', 'product_name', 'Product', 'Item Name']
    cols['product_name'] = next((col for col in product_patterns if col in df.columns), 'Product Name')
    
    return cols

# Load data execution block
with st.spinner("📊 Loading ITC InsightPulse Sales Data..."):
    df = load_data()
    st.session_state['raw_data'] = df  
    columns = detect_columns(df)
    all_kpis = calculate_kpis(df)

# Shared memory sync allocation
if 'detected_columns' not in st.session_state:
    st.session_state['detected_columns'] = columns

def reset_all_filters():
    filter_keys = ["region_filter", "brand_filter", "category_filter", "date_filter", "channel_filter"]
    for key in filter_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ================================================================
# MAIN CONTROL ROOM LAYOUT BLOCK
# ================================================================
def render_main_dashboard():
    # --- Sidebar Controls Layout ---
    st.sidebar.markdown("### 🏢 Core System Gateway")
    if st.sidebar.button("⚙️ Logout & Return to Gateway", type="primary", use_container_width=True):
        st.session_state.authenticated = False  # Log out safely on return
        st.rerun()
    st.sidebar.markdown("---")

    st.sidebar.markdown(f"""
    <div style='background: {COLORS["primary_light"]}; padding: 1rem; border-radius: 16px; margin-bottom: 1.5rem;'>
        <h2 style='color: {COLORS["white"]}; margin: 0; font-size: 1.3rem;'>🔍 Filters</h2>
        <p style='color: {COLORS["accent1"]}; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Select filters to analyze data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Region Filter Setup
    if columns['region'] in df.columns:
        regions = sorted(df[columns['region']].dropna().unique())
        selected_regions = st.sidebar.multiselect("🗺️ Region", options=regions, default=regions, key="region_filter")
    
    # Brand Filter Setup
    if columns['brand'] in df.columns:
        brands = sorted(df[columns['brand']].dropna().unique())
        selected_brands = st.sidebar.multiselect("🏷️ Brand", options=brands, default=brands[:min(5, len(brands))], key="brand_filter")

    # Product Category Filter Setup
    if 'Product Category' in df.columns:
        categories = sorted(df['Product Category'].dropna().unique())
        selected_categories = st.sidebar.multiselect("🧼 Product Category", options=categories, default=categories, key="category_filter")

    # Channel Filter Setup
    if columns['channel'] in df.columns:
        channels = sorted(df[columns['channel']].dropna().unique())
        selected_channels = st.sidebar.multiselect("🛒 Sales Channels", options=channels, default=channels, key="channel_filter")

    # Date Range Filter Setup
    st.sidebar.markdown("---")
    if columns['date'] in df.columns:
        min_date = df[columns['date']].min().date()
        max_date = df[columns['max_date'] if 'max_date' in df.columns else columns['date']].max().date()
        date_range = st.sidebar.date_input("📅 Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="date_filter")
    else:
        date_range = None

    # Reset & Refresh Control Row
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True, on_click=reset_all_filters): pass
    with col2:
        if st.button("📊 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Sidebar Data Metrics Overview Card
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style='background: {COLORS["primary_medium"]}; padding: 1rem; border-radius: 12px; border: 1px solid {COLORS["primary_light"]};'>
        <h4 style='color: {COLORS["accent1"]}; margin: 0 0 0.5rem 0;'>📈 Data Summary</h4>
        <p style='color: {COLORS["white"]}; margin: 0.2rem 0; font-size: 0.9rem;'><strong>Records:</strong> {len(df):,}</p>
        <p style='color: {COLORS["white"]}; margin: 0.2rem 0; font-size: 0.9rem;'><strong>Date Range:</strong> {df[columns['date']].min().strftime('%d-%m-%Y')} to {df[columns['date']].max().strftime('%d-%m-%Y')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Data Ingestion Filters Mutation
    filtered_df = df.copy()
    sel_reg = st.session_state.get("region_filter", None)
    sel_brd = st.session_state.get("brand_filter", None)
    sel_cat = st.session_state.get("category_filter", None)
    sel_chn = st.session_state.get("channel_filter", None)

    if sel_reg: filtered_df = filtered_df[filtered_df[columns['region']].isin(sel_reg)]
    if sel_brd: filtered_df = filtered_df[filtered_df[columns['brand']].isin(sel_brd)]
    if sel_cat and 'Product Category' in df.columns: filtered_df = filtered_df[filtered_df['Product Category'].isin(sel_cat)]
    if sel_chn and columns['channel'] in df.columns: filtered_df = filtered_df[filtered_df[columns['channel']].isin(sel_chn)]
    if date_range and len(date_range) == 2 and columns['date'] in df.columns:
        filtered_df = filtered_df[(filtered_df[columns['date']] >= pd.Timestamp(date_range[0])) & (filtered_df[columns['date']] <= pd.Timestamp(date_range[1]))]

    # Logo Decoding Hook
    logo_path = "ITC_Limited_Logo.svg.png"  
    try:
        with open(logo_path, "rb") as image_file: encoded_logo = base64.b64encode(image_file.read()).decode()
        img_src = f"data:image/png;base64,{encoded_logo}"
    except Exception: img_src = None 

    col_header1, col_header2 = st.columns([5.5, 1.5], gap="medium")
    with col_header1:
        logo_html = f"<img src='{img_src}' style='height: 55px; vertical-align: middle; margin-right: 15px; margin-bottom: 8px;'>" if img_src else "📊"
        display_min_date = date_range[0].strftime('%d-%m-%Y') if date_range else df[columns['date']].min().strftime('%d-%m-%Y')
        display_max_date = date_range[1].strftime('%d-%m-%Y') if date_range else df[columns['date']].max().strftime('%d-%m-%Y')

        st.markdown(f"""
        <div>
            <h1 style='margin: 0; display: inline-block; vertical-align: middle;'>{logo_html}ITC InsightPulse</h1>
            <p style='color: {COLORS["accent1"]}; margin: 0.4rem 0 0.5rem 0; font-size: 1.1rem; font-weight: 500;'>Interactive Sales Analytics Dashboard for PCPB Division</p>
            <div style='display: inline-block; background: rgba(20, 235, 255, 0.15); border: 1px solid {COLORS["accent2"]}; padding: 0.4rem 1rem; border-radius: 30px;'>
                <span style='color: white; font-size: 0.95rem;'>📅 Analytics Period: </span>
                <span style='color: {COLORS["accent2"]}; font-size: 0.95rem; font-weight: 700;'>{display_min_date}</span> to <span style='color: {COLORS["accent2"]}; font-size: 0.95rem; font-weight: 700;'>{display_max_date}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_header2:
        st.markdown(f"""
        <div style='text-align: center; padding: 1.2rem; background: {COLORS["primary_medium"]}; border-radius: 16px; border: 1px solid {COLORS["primary_light"]};'>
            <div style='font-size: 0.85rem; color: white; opacity: 0.8;'>Last Updated</div>
            <div style='font-size: 1.1rem; color: {COLORS["accent1"]}; font-weight: 700;'>{datetime.now().strftime('%d %b %Y')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # --- KPI Cards Visualization ---
    if not filtered_df.empty:
        kpi_metrics = calculate_kpis(filtered_df)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
        with kpi1: st.metric("💰 Total Revenue", f"₹{kpi_metrics['revenue']/1e6:.2f}M" if kpi_metrics['revenue'] >= 1e6 else f"₹{kpi_metrics['revenue']/1e3:.0f}K", delta=f"{len(filtered_df):,} transactions")
        with kpi2: st.metric("📦 Units Sold", f"{kpi_metrics['units']:,.0f}", delta=f"Avg: {kpi_metrics['units']/max(len(filtered_df), 1):.0f}/txn")
        with kpi3: st.metric("🛒 Avg Order Value", f"₹{kpi_metrics['avg_order']:,.0f}", delta="Per transaction")
        with kpi4: st.metric("📊 Sales Density", f"₹{kpi_metrics['density']:,.0f}", delta="Revenue per order")
        
        kpi5, kpi6, kpi7, kpi8 = st.columns(4, gap="medium")
        top_brand = filtered_df.groupby(columns['brand'])['Total Amount'].sum().idxmax() if columns['brand'] in filtered_df.columns else "N/A"
        top_region = filtered_df.groupby(columns['region'])['Total Amount'].sum().idxmax() if columns['region'] in filtered_df.columns else "N/A"
        
        with kpi5: st.metric("🏆 Top Brand", str(top_brand)[:15], delta="Highest revenue")
        with kpi6: st.metric("🌍 Top Region", str(top_region)[:15], delta="Best performing")
        with kpi7:
            distributor_count = filtered_df[columns['distributor']].nunique() if columns['distributor'] in filtered_df.columns else 0
            st.metric("👥 Active Distributors", f"{distributor_count}", delta="Partners")
        with kpi8: st.metric("⏱️ Date Range", f"{(filtered_df[columns['date']].max() - filtered_df[columns['date']].min()).days} days", delta="Period selected")
        
        st.markdown("---")
        
        # --- Operational Visualization Trends ---
        st.markdown("## 📈 Sales Analytics")
        st.markdown(f'<div class="analytics-box"><h3 style="color: {COLORS["accent1"]}; margin: 0 0 1.5rem 0;">Daily Revenue Trend</h3>', unsafe_allow_html=True)
        
        daily_trend = filtered_df.set_index(columns['date'])['Total Amount'].resample('D').sum().reset_index()
        daily_trend.columns = ['Date', 'Revenue']
        
        fig_trend = go.Figure(go.Scatter(x=daily_trend['Date'], y=daily_trend['Revenue'], mode='lines', line=dict(color=COLORS['accent1'], width=3), fill='tozeroy', fillcolor=COLORS['primary_light']))
        fig_trend.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0), hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['white'], family="Inter"))
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_chart1, col_chart2 = st.columns(2, gap="medium")
        with col_chart1:
            st.markdown(f'<div class="analytics-box"><h3 style="color: {COLORS["accent1"]};">Revenue by Region</h3>', unsafe_allow_html=True)
            if columns['region'] in filtered_df.columns:
                region_data = filtered_df.groupby(columns['region'])['Total Amount'].sum().sort_values()
                fig_region = go.Figure(go.Bar(y=region_data.index, x=region_data.values, orientation='h', marker=dict(color=region_data.values, colorscale=[[0, COLORS['primary_light']], [1, COLORS['accent1']]])))
                fig_region.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['white']))
                st.plotly_chart(fig_region, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_chart2:
            st.markdown(f'<div class="analytics-box"><h3 style="color: {COLORS["accent1"]};">Revenue by Brand</h3>', unsafe_allow_html=True)
            if columns['brand'] in filtered_df.columns:
                brand_data = filtered_df.groupby(columns['brand'])['Total Amount'].sum()
                fig_brand = go.Figure(go.Pie(labels=brand_data.index, values=brand_data.values, hole=0.4, marker=dict(colors=[COLORS['primary'], COLORS['accent1'], COLORS['accent2']])))
                fig_brand.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color=COLORS['white']))
                st.plotly_chart(fig_brand, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        tab1, tab2 = st.tabs(["📋 Raw Data", "📊 Statistics"])
        with tab1:
            display_cols = [col for col in [columns['date'], columns['region'], columns['brand'], columns['product_name'], columns['channel'], columns['quantity'], columns['amount']] if col in filtered_df.columns]
            st.dataframe(filtered_df[display_cols], use_container_width=True, height=400)
        with tab2:
            st.markdown(f'<div class="analytics-box"><h3 style="color: {COLORS["accent1"]};">Statistical Metrics</h3>', unsafe_allow_html=True)
            st.write(f"Total Transactions Processed: {len(filtered_df):,}")
            st.write(f"Mean Order Yield bill value: ₹{filtered_df[columns['amount']].mean():,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ No data matches the selected filters.")

    # --- Footer ---
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: {COLORS["white"]}; padding: 3rem 2rem; background: linear-gradient(135deg, {COLORS["dark_primary"]}, {COLORS["darker"]}); border-radius: 24px;'>
        <h2 style='color: {COLORS["accent1"]}; margin: 0;'>🚀 ITC InsightPulse Control Room</h2>
        <p style='opacity:0.8;'>Interactive Corporate Analytics Framework | © {datetime.now().year} ITC Limited</p>
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# EXECUTE UI RENDERING ON ROUTE TARGET CALL NATIVELY
# ================================================================
# FIXED FROM PREVIOUS ROUTER ERROR: Invokes layout directly since main app.py controls navigation tree
render_main_dashboard()