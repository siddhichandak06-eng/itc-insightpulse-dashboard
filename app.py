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
from dotenv import load_dotenv
load_dotenv() 

warnings.filterwarnings("ignore")


# ================================================================
# PAGE CONFIG
# ================================================================
st.set_page_config(
    page_title="ITC InsightPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Save COLORS to session state so sub-pages can look exactly the same
if 'COLORS' not in st.session_state:
    st.session_state.COLORS = COLORS

# ================================================================
# CUSTOM CSS STYLING
# ================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {{
    font-family: 'Inter', sans-serif;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: linear-gradient(135deg, #000000 0%, #0a1f44 50%, #001f54 100%);
    background-attachment: fixed;
}}

[data-testid="stMain"] {{
    background: transparent;
    padding-top: 2rem;
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['dark_primary']} 100%);
    border-right: 1px solid {COLORS['primary_light']};
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    color: {COLORS['white']} !important;
}}

[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
    color: {COLORS['white']} !important;
}}

[data-testid="stSidebar"] .stMarkdown {{
    color: {COLORS['white']} !important;
}}

/* Forcing Times New Roman on the Main Title Element */
h1, 
h1 span,
.stHeadingWithAnchor h1,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMain"] h1 {{
    font-family: 'Times New Roman', Times, Baskerville, Georgia, serif !important;
    font-weight: 800 !important;
    font-size: 2.8rem !important;
    letter-spacing: 0.02em !important;
    background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent2']}) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    color: transparent !important;
}}

h2 {{
    color: {COLORS['white']} !important;
    font-weight: 700 !important;
    font-size: 1.8rem !important;
}}

h3 {{
    color: {COLORS['accent1']} !important;
    font-weight: 600 !important;
}}

p {{
    color: {COLORS['white']} !important;
}}

.stMetric {{
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(20px) !important;
    border-radius: 16px !important;
    border: 1px solid {COLORS['primary_medium']} !important;
    padding: 1.5rem !important;
    box-shadow: 0 20px 40px {COLORS['primary_light']};
    transition: all 0.3s ease !important;
}}

.stMetric:hover {{
    transform: translateY(-5px) !important;
    box-shadow: 0 30px 60px {COLORS['primary_medium']};
    border-color: {COLORS['accent1']} !important;
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
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent1']}, {COLORS['accent2']});
    border-radius: 20px 20px 0 0;
}}

.analytics-box:hover {{
    transform: translateY(-5px) !important;
    box-shadow: 0 30px 60px {COLORS['primary_medium']};
    border-color: {COLORS['accent1']} !important;
}}

.stButton > button {{
    background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent1']}) !important;
    color: {COLORS['white']} !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 24px {COLORS['primary_light']};
}}

.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px {COLORS['primary_medium']};
}}

[data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 2px solid {COLORS['primary_light']} !important;
}}

[data-testid="stTabs"] [role="tab"] {{
    color: {COLORS['white']} !important;
    border-bottom: 3px solid transparent !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: {COLORS['accent1']} !important;
    border-bottom-color: {COLORS['accent1']} !important;
}}

.stDataFrame {{
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid {COLORS['primary_light']} !important;
    border-radius: 12px !important;
}}

.streamlit-expanderHeader {{
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid {COLORS['primary_light']} !important;
    border-radius: 10px !important;
}}

.streamlit-expanderHeader p {{
    color: {COLORS['white']} !important;
    font-weight: 600 !important;
}}

.stSelectbox label, .stMultiSelect label, .stDateInput label {{
    color: {COLORS['white']} !important;
    font-weight: 600 !important;
}}

[data-testid="stSelectbox"] [role="button"],
[data-testid="stMultiSelect"] [role="button"] {{
    background: rgba(20, 121, 255, 0.1) !important;
    border: 1px solid {COLORS['primary_medium']} !important;
    color: {COLORS['white']} !important;
    border-radius: 8px !important;
}}

/* Navigation Menu Custom Formatting */
[data-testid="stSidebarNavItems"] div {{
    color: {COLORS['gray']} !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1rem !important;
    text-transform: uppercase !important;
    margin-top: 1rem !important;
    margin-bottom: 0.25rem !important;
    padding-left: 0.5rem !important;
}}

[data-testid="stSidebarNavItems"] a {{
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(20, 121, 255, 0.1) !important;
    border-radius: 8px !important;
    margin: 0.3rem 0 !important;
    padding: 0.5rem 0.75rem !important;
    transition: all 0.3s ease !important;
}}

[data-testid="stSidebarNavItems"] a:hover {{
    background: {COLORS['primary_light']} !important;
    border-color: {COLORS['accent1']} !important;
    transform: translateX(4px);
}}

[data-testid="stSidebarNavItems"] a[aria-current="page"] {{
    background: linear-gradient(90deg, {COLORS['primary_medium']}, transparent) !important;
    border-left: 4px solid {COLORS['accent1']} !important;
    border-color: {COLORS['primary_medium']} !important;
}}

[data-testid="stSidebarNavItems"] a span {{
    color: {COLORS['white']} !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
}}
</style>
""", unsafe_allow_html=True)

# ================================================================
# DATABASE CONNECTION
# ================================================================
@st.cache_resource
def init_connection():
    """Initialize and cache database connection securely"""
    try:
        # Fallback defaults provided if environment variables aren't set
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")  
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_NAME = os.getenv("DB_NAME", "itc_sales_db")

        connection_string = f"mysql+pymysql://{DB_USER}:{urllib.parse.quote_plus(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}"
        engine = sa.create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Database Connection Error: {str(e)}")
        st.stop()

# ================================================================
# DATA LOADING & CACHING
# ================================================================
@st.cache_data(ttl=300)
def load_data():
    """Load data from MySQL with validation"""
    try:
        query = "SELECT * FROM sales_data LIMIT 100000"
        
        # 🟢 FIX: Extract engine safely from session state instead of the raw variable
        current_engine = st.session_state.get('db_engine')
        if current_engine is None:
            current_engine = init_connection()
            
        df = pd.read_sql(query, current_engine)
        
        # Data cleaning
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
        
        # Numeric columns
        numeric_cols = ['Quantity', 'Total Amount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        
        # Remove negative values
        if 'Total Amount' in df.columns and 'Quantity' in df.columns:
            df = df[(df['Total Amount'] >= 0) & (df['Quantity'] >= 0)]
        
        return df.sort_values('Date') if 'Date' in df.columns else df
    
    except Exception as e:
        st.error(f"❌ Data Loading Error: {str(e)}")
        st.stop()

@st.cache_data(ttl=300)
def calculate_kpis(df):
    """Calculate all KPI metrics"""
    if df.empty:
        return {col: 0 for col in ['revenue', 'units', 'transactions', 'avg_order', 'growth', 'density']}
    
    return {
        'revenue': df['Total Amount'].sum() if 'Total Amount' in df.columns else 0,
        'units': df['Quantity'].sum() if 'Quantity' in df.columns else 0,
        'transactions': len(df),
        'avg_order': df['Total Amount'].mean() if 'Total Amount' in df.columns else 0,
        'growth': 0,  
        'density': df['Total Amount'].sum() / len(df) if len(df) > 0 else 0
    }

def detect_columns(df):
    """Auto-detect column names from dataframe"""
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
    
    return cols

# Load data
with st.spinner("📊 Loading ITC InsightPulse Sales Data..."):
    df = load_data()
    columns = detect_columns(df)
    all_kpis = calculate_kpis(df)

# Share the raw dataframe globally inside the Session State
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = df

# Extract static boundaries for front header display
min_date_raw = df[columns['date']].min().strftime('%d %b %Y')
max_date_raw = df[columns['date']].max().strftime('%d %b %Y')

# ================================================================
# FILTER STATE MANAGER RESET CALLBACK
# ================================================================
def reset_all_filters():
    filter_keys = ["region_filter", "brand_filter", "category_filter", "date_filter"]
    for key in filter_keys:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ================================================================
# MAIN CONTROL ROOM VIEW FUNCTION
# ================================================================
def render_main_dashboard():
    # --- Sidebar Controls (Nested inside the render loop to prevent duplicate key errors) ---
    st.sidebar.markdown(f"""
    <div style='background: {COLORS["primary_light"]}; padding: 1rem; border-radius: 16px; margin-bottom: 1.5rem;'>
        <h2 style='color: {COLORS["white"]}; margin: 0; font-size: 1.3rem;'>🔍 Filters</h2>
        <p style='color: {COLORS["accent1"]}; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>Select filters to analyze data</p>
    </div>
    """, unsafe_allow_html=True)

    # Region Filter
    if columns['region'] in df.columns:
        regions = sorted(df[columns['region']].dropna().unique())
        selected_regions = st.sidebar.multiselect(
            "🗺️ Region",
            options=regions,
            default=regions,
            key="region_filter"
        )
    else:
        selected_regions = None
        st.sidebar.warning("Region column not found")

    # Brand Filter
    if columns['brand'] in df.columns:
        brands = sorted(df[columns['brand']].dropna().unique())
        selected_brands = st.sidebar.multiselect(
            "🏷️ Brand",
            options=brands,
            default=brands[:min(5, len(brands))],
            key="brand_filter"
        )
    else:
        selected_brands = None
        st.sidebar.warning("Brand column not found")

    # Product Category Filter
    if 'Product Category' in df.columns:
        categories = sorted(df['Product Category'].dropna().unique())
        selected_categories = st.sidebar.multiselect(
            "🧼 Product Category",
            options=categories,
            default=categories,
            key="category_filter"
        )
    else:
        selected_categories = None
        st.sidebar.warning("Product Category column not found")

    # Date Range Filter
    st.sidebar.markdown("---")
    if columns['date'] in df.columns:
        min_date = df[columns['date']].min().date()
        max_date = df[columns['date']].max().date()
        
        date_range = st.sidebar.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_filter"
        )
    else:
        date_range = None

    # Reset Filters Button
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True, on_click=reset_all_filters):
            pass

    with col2:
        if st.button("📊 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Sidebar Info
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style='background: {COLORS["primary_medium"]}; padding: 1rem; border-radius: 12px; border: 1px solid {COLORS["primary_light"]};'>
        <h4 style='color: {COLORS["accent1"]}; margin: 0 0 0.5rem 0;'>📈 Data Summary</h4>
        <p style='color: {COLORS["white"]}; margin: 0.2rem 0; font-size: 0.9rem;'>
            <strong>Records:</strong> {len(df):,}
        </p>
        <p style='color: {COLORS["white"]}; margin: 0.2rem 0; font-size: 0.9rem;'>
            <strong>Date Range:</strong> {df[columns['date']].min().strftime('%d-%m-%Y')} to {df[columns['date']].max().strftime('%d-%m-%Y')}
        </p>
        <p style='color: {COLORS["white"]}; margin: 0.2rem 0; font-size: 0.9rem;'>
            <strong>Updated:</strong> {datetime.now().strftime('%H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- Apply Filters ---
    filtered_df = df.copy()

    # We read directly from session_state if available to force instant sync on Reset click
    sel_reg = st.session_state.get("region_filter", regions)
    sel_brd = st.session_state.get("brand_filter", brands[:min(5, len(brands))])
    sel_cat = st.session_state.get("category_filter", categories) if 'Product Category' in df.columns else None

    if sel_reg:
        filtered_df = filtered_df[filtered_df[columns['region']].isin(sel_reg)]

    if sel_brd:
        filtered_df = filtered_df[filtered_df[columns['brand']].isin(sel_brd)]

    if sel_cat:
        filtered_df = filtered_df[filtered_df['Product Category'].isin(sel_cat)]

    if date_range and len(date_range) == 2 and columns['date'] in df.columns:
        filtered_df = filtered_df[
            (filtered_df[columns['date']] >= pd.Timestamp(date_range[0])) &
            (filtered_df[columns['date']] <= pd.Timestamp(date_range[1]))
        ]

    # ================================================================
    # HEADER SECTION WITH LOCAL LOGO ENCODING
    # ================================================================
    import base64

    # 1. Safely read and encode your local ITC logo file to base64 format
    logo_path = "ITC_Limited_Logo.svg.png"  
    
    try:
        with open(logo_path, "rb") as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode()
        # Create a browser-readable source string
        img_src = f"data:image/png;base64,{encoded_logo}"
    except Exception:
        # Fallback to a data chart emoji if the path or file is missing
        img_src = None 

    # 2. Render the layout columns (Adjusted sizes so title + logo has more space)
    col_header1, col_header2 = st.columns([5.5, 1.5], gap="medium")

    with col_header1:
        # Build an inline container so the image and text sit side-by-side
        if img_src:
            logo_html = f"<img src='{img_src}' style='height: 55px; vertical-align: middle; margin-right: 15px; margin-bottom: 8px;'>"
        else:
            logo_html = "<span style='font-size: 2.5rem; vertical-align: middle; margin-right: 15px;'>📊</span>"

        st.markdown(f"""
        <div>
            <h1 style='margin: 0; display: inline-block; vertical-align: middle;'>
                {logo_html}ITC InsightPulse
            </h1>
            <p style='color: {COLORS["accent1"]}; margin: 0.4rem 0 0.5rem 0; font-size: 1.1rem; font-weight: 500;'>
                Interactive Sales Analytics Dashboard for PCPB Division
            </p>
            <div style='display: inline-block; background: rgba(20, 235, 255, 0.15); border: 1px solid {COLORS["accent2"]}; padding: 0.4rem 1rem; border-radius: 30px;'>
                <span style='color: white; font-size: 0.95rem; font-weight: 600;'>📅 Analytics Period: </span>
                <span style='color: {COLORS["accent2"]}; font-size: 0.95rem; font-weight: 700;'>{min_date_raw}</span>
                <span style='color: white; font-size: 0.95rem;'> to </span>
                <span style='color: {COLORS["accent2"]}; font-size: 0.95rem; font-weight: 700;'>{max_date_raw}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_header2:
        st.markdown(f"""
        <div style='text-align: center; padding: 1.2rem; background: {COLORS["primary_medium"]}; border-radius: 16px; border: 1px solid {COLORS["primary_light"]};'>
            <div style='font-size: 0.85rem; color: white; opacity: 0.8;'>Last Updated</div>
            <div style='font-size: 1.1rem; color: {COLORS["accent1"]}; font-weight: 700; margin: 0.3rem 0;'>
                {datetime.now().strftime('%d %b %Y')}
            </div>
            <div style='font-size: 0.8rem; color: white; opacity: 0.7;'>
                {datetime.now().strftime('%H:%M:%S')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # ================================================================
    # KPI CARDS - INTELLIGENT DASHBOARD
    # ================================================================
    if not filtered_df.empty:
        kpi_metrics = calculate_kpis(filtered_df)
        
        # Row 1
        kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
        
        with kpi1:
            st.metric(
                label="💰 Total Revenue",
                value=f"₹{kpi_metrics['revenue']/1e6:.2f}M" if kpi_metrics['revenue'] >= 1e6 else f"₹{kpi_metrics['revenue']/1e3:.0f}K",
                delta=f"{len(filtered_df):,} transactions"
            )
        
        with kpi2:
            st.metric(
                label="📦 Units Sold",
                value=f"{kpi_metrics['units']:,.0f}",
                delta=f"Avg: {kpi_metrics['units']/max(len(filtered_df), 1):.0f}/txn"
            )
        
        with kpi3:
            st.metric(
                label="🛒 Avg Order Value",
                value=f"₹{kpi_metrics['avg_order']:,.0f}",
                delta="Per transaction"
            )
        
        with kpi4:
            st.metric(
                label="📊 Sales Density",
                value=f"₹{kpi_metrics['density']:,.0f}",
                delta="Revenue per order"
            )
        
        # Row 2
        kpi5, kpi6, kpi7, kpi8 = st.columns(4, gap="medium")
        
        if columns['brand'] in filtered_df.columns:
            top_brand = filtered_df.groupby(columns['brand'])['Total Amount'].sum().idxmax()
        else:
            top_brand = "N/A"
        
        if columns['region'] in filtered_df.columns:
            top_region = filtered_df.groupby(columns['region'])['Total Amount'].sum().idxmax()
        else:
            top_region = "N/A"
        
        with kpi5:
            st.metric(
                label="🏆 Top Brand",
                value=str(top_brand)[:15],
                delta="Highest revenue"
            )
        
        with kpi6:
            st.metric(
                label="🌍 Top Region",
                value=str(top_region)[:15],
                delta="Best performing"
            )
        
        with kpi7:
            distributor_count = filtered_df[columns['distributor']].nunique() if columns['distributor'] in filtered_df.columns else 0
            st.metric(
                label="👥 Active Distributors",
                value=f"{distributor_count}",
                delta="Partners"
            )
        
        with kpi8:
            st.metric(
                label="⏱️ Date Range",
                value=f"{(filtered_df[columns['date']].max() - filtered_df[columns['date']].min()).days} days",
                delta="Period selected"
            )
        
        st.markdown("---")
        
        # ================================================================
        # ANALYTICS CHARTS
        # ================================================================
        st.markdown("## 📈 Sales Analytics")
        
        # Chart 1: Revenue Trend
        st.markdown(f"""
        <div class="analytics-box">
            <h3 style='color: {COLORS["accent1"]}; margin: 0 0 1.5rem 0;'>Daily Revenue Trend</h3>
        """, unsafe_allow_html=True)
        
        daily_trend = filtered_df.set_index(columns['date'])['Total Amount'].resample('D').sum().reset_index()
        daily_trend.columns = ['Date', 'Revenue']
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=daily_trend['Date'],
            y=daily_trend['Revenue'],
            mode='lines',
            name='Revenue',
            line=dict(color=COLORS['accent1'], width=3),
            fill='tozeroy',
            fillcolor=COLORS['primary_light'],
            hovertemplate='<b>%{x|%d %b %Y}</b><br>₹%{y:,.0f}<extra></extra>'
        ))
        
        fig_trend.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=0, b=0),
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['white'], family="Inter"),
            xaxis=dict(showgrid=True, gridcolor=COLORS['primary_light']),
            yaxis=dict(showgrid=True, gridcolor=COLORS['primary_light']),
            legend=dict(y=1.1, x=0)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True, config={'responsive': True})
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Charts 2 & 3: Region & Brand
        col_chart1, col_chart2 = st.columns(2, gap="medium")
        
        with col_chart1:
            st.markdown(f"""
            <div class="analytics-box">
                <h3 style='color: {COLORS["accent1"]}; margin: 0 0 1.5rem 0;'>Revenue by Region</h3>
            """, unsafe_allow_html=True)
            
            if columns['region'] in filtered_df.columns:
                region_data = filtered_df.groupby(columns['region'])['Total Amount'].sum().sort_values()
                
                fig_region = go.Figure(data=[
                    go.Bar(
                        y=region_data.index,
                        x=region_data.values,
                        orientation='h',
                        marker=dict(
                            color=region_data.values,
                            colorscale=[[0, COLORS['primary_light']], [1, COLORS['accent1']]],
                            line=dict(color=COLORS['primary_medium'], width=1)
                        ),
                        text=['₹' + f"{val/1e6:.1f}M" if val >= 1e6 else '₹' + f"{val/1e3:.0f}K" for val in region_data.values],
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>'
                    )
                ])
                
                fig_region.update_layout(
                    height=400,
                    margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['white']),
                    xaxis_title='',
                    yaxis_title=''
                )
                
                st.plotly_chart(fig_region, use_container_width=True, config={'responsive': True})
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_chart2:
            st.markdown(f"""
            <div class="analytics-box">
                <h3 style='color: {COLORS["accent1"]}; margin: 0 0 1.5rem 0;'>Revenue by Brand</h3>
            """, unsafe_allow_html=True)
            
            if columns['brand'] in filtered_df.columns:
                brand_data = filtered_df.groupby(columns['brand'])['Total Amount'].sum()
                
                fig_brand = go.Figure(data=[
                    go.Pie(
                        labels=brand_data.index,
                        values=brand_data.values,
                        hole=0.4,
                        marker=dict(colors=[COLORS['primary'], COLORS['accent1'], COLORS['accent2']]),
                        textposition='inside',
                        textinfo='label+percent',
                        hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>'
                    )
                ])
                
                fig_brand.update_layout(
                    height=400,
                    margin=dict(l=0, r=0, t=0, b=0),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['white'])
                )
                
                st.plotly_chart(fig_brand, use_container_width=True, config={'responsive': True})
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Chart 4: Top Distributors
        st.markdown(f"""
        <div class="analytics-box">
            <h3 style='color: {COLORS["accent1"]}; margin: 0 0 1.5rem 0;'>Top Distributors</h3>
        """, unsafe_allow_html=True)
        
        if columns['distributor'] in filtered_df.columns:
            top_distributors = filtered_df.groupby(columns['distributor'])['Total Amount'].sum().nlargest(10).sort_values()
            
            fig_dist = go.Figure(data=[
                go.Bar(
                    y=top_distributors.index,
                    x=top_distributors.values,
                    orientation='h',
                    marker=dict(
                        color=top_distributors.values,
                        colorscale=[[0, COLORS['primary_light']], [1, COLORS['accent2']]],
                        line=dict(color=COLORS['primary_medium'], width=1)
                    ),
                    text=['₹' + f"{val/1e6:.1f}M" if val >= 1e6 else '₹' + f"{val/1e3:.0f}K" for val in top_distributors.values],
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>'
                )
            ])
            
            fig_dist.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['white']),
                xaxis_title='',
                yaxis_title=''
            )
            
            st.plotly_chart(fig_dist, use_container_width=True, config={'responsive': True})
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ================================================================
        # DETAILED ANALYSIS TABS
        # ================================================================
        st.markdown("---")
        st.markdown("## 🔍 Detailed Analysis")
        
        tab1, tab2, tab3 = st.tabs(["📋 Raw Data", "📊 Statistics", "📈 Comparisons"])
        
        with tab1:
            st.markdown(f"""
            <div class="analytics-box">
                <h3 style='color: {COLORS["accent1"]};'>Transaction Details</h3>
                <p style='color: {COLORS["white"]}; opacity: 0.8;'>Total Records: {len(filtered_df):,}</p>
            </div>
            """, unsafe_allow_html=True)
            
            display_cols = [col for col in [columns['date'], columns['region'], columns['brand'], 
                                           columns['quantity'], columns['amount']] 
                           if col in filtered_df.columns]
            
            display_df = filtered_df[display_cols].copy()
            display_df[columns['date']] = pd.to_datetime(display_df[columns['date']]).dt.strftime('%d-%m-%Y')
            display_df[columns['amount']] = display_df[columns['amount']].apply(lambda x: f'₹{x:,.2f}')
            
            st.dataframe(display_df, use_container_width=True, height=600)
            
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with tab2:
            st.markdown(f"""
            <div class="analytics-box">
                <h3 style='color: {COLORS["accent1"]};'>Statistical Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            with stat_col1:
                st.markdown(f"**Revenue Statistics**")
                st.write(f"Max: ₹{filtered_df[columns['amount']].max():,.2f}")
                st.write(f"Min: ₹{filtered_df[columns['amount']].min():,.2f}")
                st.write(f"Median: ₹{filtered_df[columns['amount']].median():,.2f}")
                st.write(f"Std Dev: ₹{filtered_df[columns['amount']].std():,.2f}")
            
            with stat_col2:
                st.markdown(f"**Quantity Statistics**")
                st.write(f"Max: {filtered_df[columns['quantity']].max():,.0f} units")
                st.write(f"Min: {filtered_df[columns['quantity']].min():,.0f} units")
                st.write(f"Median: {filtered_df[columns['quantity']].median():,.0f} units")
                st.write(f"Avg: {filtered_df[columns['quantity']].mean():,.2f}")
            
            with stat_col3:
                st.markdown(f"**Data Summary**")
                st.write(f"Total Records: {len(filtered_df):,}")
                if columns['region'] in filtered_df.columns:
                    st.write(f"Regions: {filtered_df[columns['region']].nunique()}")
                if columns['brand'] in filtered_df.columns:
                    st.write(f"Brands: {filtered_df[columns['brand']].nunique()}")
                if columns['distributor'] in filtered_df.columns:
                    st.write(f"Distributors: {filtered_df[columns['distributor']].nunique()}")
        
        with tab3:
            st.markdown(f"""
            <div class="analytics-box">
                <h3 style='color: {COLORS["accent1"]};'>30-Day Performance Comparison</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if columns['date'] in filtered_df.columns:
                end_date = filtered_df[columns['date']].max()
                last_30 = filtered_df[(filtered_df[columns['date']] >= end_date - timedelta(days=30))]
                prev_30 = filtered_df[(filtered_df[columns['date']] >= end_date - timedelta(days=60)) & 
                                    (filtered_df[columns['date']] < end_date - timedelta(days=30))]
                
                comp_data = pd.DataFrame({
                    'Period': ['Last 30 Days', 'Previous 30 Days'],
                    'Revenue': [
                        last_30[columns['amount']].sum() if len(last_30) > 0 else 0,
                        prev_30[columns['amount']].sum() if len(prev_30) > 0 else 0
                    ],
                    'Transactions': [len(last_30), len(prev_30)]
                })
                
                fig_comp = px.bar(
                    comp_data,
                    x='Period',
                    y=['Revenue', 'Transactions'],
                    barmode='group',
                    color_discrete_sequence=[COLORS['accent1'], COLORS['accent2']]
                )
                
                fig_comp.update_layout(
                    height=450,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['white']),
                    legend=dict(y=1.1)
                )
                
                st.plotly_chart(fig_comp, use_container_width=True)

    else:
        st.warning("⚠️ No data matches the selected filters. Please adjust your filter selections.")

    # ================================================================
    # FOOTER
    # ================================================================
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: {COLORS["white"]}; padding: 3rem 2rem; 
                background: linear-gradient(135deg, {COLORS["dark_primary"]}, {COLORS["darker"]});
                border-radius: 24px; margin: 2rem 0 0 0; border: 1px solid {COLORS["primary_light"]};'>
        <h2 style='color: {COLORS["accent1"]}; margin: 0 0 1rem 0;'>🚀 ITC InsightPulse</h2>
        <p style='margin: 0 0 1rem 0; opacity: 0.9; font-size: 1rem;'>Interactive Sales Analytics Dashboard for PCPB Division | Powered by Advanced Analytics</p>
        <div style='display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;'>
            <div style='color: {COLORS["accent2"]};'>
                📊 Last Updated: {datetime.now().strftime("%d %B %Y %H:%M:%S")}
            </div>
            <div style='color: {COLORS["white"]}; opacity: 0.8;'>
                Built with <strong>Streamlit</strong> • <strong>Plotly</strong> • <strong>MySQL</strong>
            </div>
            <div style='color: {COLORS["accent1"]};'>
                © {datetime.now().year} ITC Limited
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# CORE SYSTEM MULTI-PAGE LAYOUT ROUTER (With Custom Brand Files)
# ================================================================
# 1. Main Dashboard Target Setup
main_dashboard = st.Page(
    render_main_dashboard, 
    title="Master Sales Control Room", 
    icon="🏢", 
    default=True
)

# 2. Strategic Lab Targets Setup (Points directly to your core tool files)
planning_hub = st.Page(
    "pages/planning_hub.py", 
    title="Business Planning Hub", 
    icon="🔮"
)

fund_allocator = st.Page(
    "pages/fund_allocator.py", 
    title="Strategic Fund Allocator", 
    icon="💰"
)

brand_correlation= st.Page(
    "pages/brand_correlation.py", 
    title="Brand Correlation", 
    icon="🏷️"
)

# 3. Dynamic Loop to find your custom individual brand files
brand_diagnostic_pages = []

if os.path.exists("pages"):
    for file in sorted(os.listdir("pages")):
        # Only look for python files, and ignore our main utility pages
        if file.endswith(".py") and file not in ["planning_hub.py", "fund_allocator.py", "brand_correlation.py"]:
            page_path = f"pages/{file}"
            
            # Clean up the filename to make a pretty title (e.g., 'fiama_di_wills.py' -> 'Fiama Di Wills')
            clean_title = file.replace(".py", "").replace("_", " ").title()
            
            # Create the page object and add it to our list
            brand_page = st.Page(page_path, title=clean_title, icon="🏷️")
            brand_diagnostic_pages.append(brand_page)

# 4. Bind all modules into clean navigation dropdown categories
navigation_ecosystem = st.navigation({
    "Executive Control Room": [main_dashboard],
    "Strategic Analysis Labs": [planning_hub, fund_allocator, brand_correlation],
    "Brand Diagnostics Suite": brand_diagnostic_pages
})

# Run the unified router app
navigation_ecosystem.run()