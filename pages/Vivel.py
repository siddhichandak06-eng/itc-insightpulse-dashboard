import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Grab global configuration/cache from app.py session state
if 'raw_data' in st.session_state:
    df = st.session_state.raw_data
    COLORS = st.session_state.COLORS
else:
    st.error("Please run the main dashboard (app.py) first to initialize data strings.")
    st.stop()

# Force Times New Roman styling onto individual brand headers
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
html, body, [data-testid="stAppViewContainer"] {{ background: linear-gradient(135deg, #000000 0%, #0a1f44 50%, #001f54 100%) fixed; }}
[data-testid="stMain"] {{ background: transparent; padding-top: 2rem; }}
h1, [data-testid="stMain"] h1, [data-testid="stMarkdownContainer"] h1 {{
    font-family: 'Times New Roman', Times, serif !important;
    font-weight: 800 !important; font-size: 2.8rem !important;
    background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent2']}) !important;
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; background-clip: text !important; color: transparent !important;
}}
.stMetric {{ background: rgba(255,255,255,0.08) !important; border-radius: 16px !important; border: 1px solid {COLORS['primary_medium']} !important; padding: 1.5rem !important; }}
.analytics-box {{ background: rgba(255,255,255,0.08) !important; border-radius: 20px !important; border: 1px solid {COLORS['primary_medium']} !important; padding: 2rem !important; margin: 1.5rem 0 !important; position: relative; }}
.analytics-box::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, {COLORS['accent1']}, {COLORS['accent2']}); border-radius: 20px 20px 0 0; }}
p {{ color: white; }}
</style>
""", unsafe_allow_html=True)

# Set the static brand focus context for this page file
BRAND_NAME = "Vivel"

# Filter the dataset exclusively for this brand
brand_df = df[df['Brand'] == BRAND_NAME]

# --- UI Header ---
st.markdown(f"<h1>{BRAND_NAME} Performance Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: {{COLORS['accent1']}}; font-size: 1.1rem;'>Dedicated Performance Insights & Diagnostic Metrics Suite</p>", unsafe_allow_html=True)
st.markdown("---")

if not brand_df.empty:
    # --- Metrics calculations ---
    total_revenue = brand_df['Total Amount'].sum()
    units_sold = brand_df['Quantity'].sum()
    avg_txn = brand_df['Total Amount'].mean()
    
    m1, m2, m3 = st.columns(3)
    with m1:
        val_str = f"₹{total_revenue/1e6:.2f}M" if total_revenue >= 1e6 else f"₹{total_revenue/1e3:.1f}K"
        st.metric(label="Gross Revenue", value=val_str)
    with m2:
        st.metric(label="Total Volume Sold", value=f"{units_sold:,.0f} units")
    with m3:
        st.metric(label="Average Transaction Size", value=f"₹{avg_txn:,.2f}")

    # --- Regional Contribution Plot ---
    st.markdown('<div class="analytics-box">', unsafe_allow_html=True)
    st.markdown("<h3>Regional Distribution Matrix</h3>", unsafe_allow_html=True)
    if 'Region' in brand_df.columns:
        region_summary = brand_df.groupby('Region')['Total Amount'].sum().reset_index()
        fig_reg = px.bar(region_summary, x='Region', y='Total Amount', color='Total Amount',
                         color_continuous_scale=[COLORS['dark_primary'], COLORS['accent1']])
        fig_reg.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_reg, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Top Distributors Plot ---
    st.markdown('<div class="analytics-box">', unsafe_allow_html=True)
    st.markdown("<h3>Top Strategic Channel Distributors</h3>", unsafe_allow_html=True)
    if 'Distributor' in brand_df.columns:
        dist_summary = brand_df.groupby('Distributor')['Total Amount'].sum().nlargest(5).reset_index()
        fig_dist = px.bar(dist_summary, x='Total Amount', y='Distributor', orientation='h', color='Total Amount',
                          color_continuous_scale=[COLORS['dark_primary'], COLORS['accent2']])
        fig_dist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_dist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning(f"⚠️ No transactional logs found for {BRAND_NAME} within the selected parameters.")
