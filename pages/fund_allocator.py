"""
ITC PCPB FUND ALLOCATOR - v3.0 (Denominations & Manager Insights)
===================================================================
Features:
- Budget input selection in Lakhs or Crores INR.
- Automatic equal distribution baseline.
- Manager recommendation highlighting the most profitable brand.
- Interactive brand fund allocation and expected ROI visualization.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ================================================================
# THEME & COLORS SAFE BACKUP
# ================================================================
COLORS = st.session_state.get('COLORS')
if not COLORS:
    COLORS = {
        'primary': '#1f77b4',
        'accent_bright': '#ff7f0e',
        'success': '#2ca02c',
        'warning': '#bcbd22',
        'danger': '#d62728',
        'white': '#ffffff',
        'dark_secondary': '#121212'
    }

# ================================================================
# DATA ACCESS
# ================================================================
if 'raw_data' in st.session_state:
    df = st.session_state['raw_data']
else:
    st.error("Please start from the main dashboard.")
    st.stop()

# ================================================================
# HISTORICAL DATA ANALYSIS & PROFITABILITY CALCULATION
# ================================================================
df_calc = df.copy()
df_calc['Date'] = pd.to_datetime(df_calc['Date'])
today = df_calc['Date'].max()
last_30 = today - timedelta(days=30)
previous_30 = last_30 - timedelta(days=30)

recent_df = df_calc[(df_calc['Date'] >= last_30)]
previous_df = df_calc[(df_calc['Date'] >= previous_30) & (df_calc['Date'] < last_30)]

brand_metrics = df_calc.groupby('Brand').agg(
    revenue=('Total Amount', 'sum'),
    units=('Quantity', 'sum')
).reset_index()

recent_revenue = recent_df.groupby('Brand')['Total Amount'].sum()
previous_revenue = previous_df.groupby('Brand')['Total Amount'].sum()

brand_metrics['growth_30d'] = brand_metrics['Brand'].apply(
    lambda x: ((recent_revenue.get(x, 0) - previous_revenue.get(x, 0)) / max(previous_revenue.get(x, 1), 1) * 100)
)
# ROI Efficiency multiplier
brand_metrics['roi_score'] = (brand_metrics['revenue'] / (brand_metrics['units'] + 1)) * 100

# Identify the most profitable brand
most_profitable_brand = brand_metrics.sort_values('roi_score', ascending=False).iloc[0]['Brand']

# ================================================================
# PAGE HEADER & MANAGER INSIGHT
# ================================================================
st.markdown("# 💰 Fund Allocator Dashboard")
st.markdown("*Strategic capital distribution engine for Division Managers*")

# Distinct box indicating profitability recommendation
st.markdown(f"""
<div style='background-color:rgba(31, 119, 180, 0.15); border-left: 6px solid {COLORS['primary']}; padding:15px; border-radius:4px; margin-bottom:20px;'>
    <h4 style='margin:0; color:{COLORS['white']};'>💡 Division Manager Strategy Insight</h4>
    <p style='margin:5px 0 0 0; font-size:1.05rem;'>
        Based on historical revenue-per-unit metrics and recent velocity, channeling additional capital into 
        <strong>{most_profitable_brand}</strong> yields the highest profitability efficiency.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ================================================================
# STATE INITIALIZATION (DEFAULT EQUALLY DISTRIBUTABLE BASELINE)
# ================================================================
brands = ['Dermafique', 'Engage', 'Fiama', 'Savlon', 'Vivel']

# Ensure it resets to equal distribution by default upon initialization
for b in brands:
    if f"alloc_{b}" not in st.session_state:
        st.session_state[f"alloc_{b}"] = 20

# ================================================================
# CONFIGURATION: BUDGET UNIT SELECTOR (LAKHS / CRORES)
# ================================================================
st.markdown("### ⚙️ Step 1: Define Total Budget Pool")
unit_choice = st.radio(
    "Choose Budget Currency Denomination:",
    ["Lakhs (₹ Input)", "Crores (₹ Input)", "Absolute Amount (₹ Direct)"],
    horizontal=True
)

if unit_choice == "Lakhs (₹ Input)":
    budget_input = st.number_input("Enter Budget amount in Lakhs (1 Lakh = ₹1,00,000)", min_value=1.0, max_value=5000.0, value=100.0, step=5.0)
    total_budget = budget_input * 100000
    formatted_budget = f"₹{budget_input:.2f} Lakhs"
elif unit_choice == "Crores (₹ Input)":
    budget_input = st.number_input("Enter Budget amount in Crores (1 Crore = ₹1,00,00,000)", min_value=0.1, max_value=100.0, value=1.0, step=0.5)
    total_budget = budget_input * 10000000
    formatted_budget = f"₹{budget_input:.2f} Crores"
else:
    total_budget = st.number_input("Enter Budget Amount directly (₹)", min_value=10000, max_value=1000000000, value=10000000, step=50000)
    formatted_budget = f"₹{total_budget:,.2f}"

st.caption(f"Current Working Budget Pool initialized to: **{formatted_budget}** (Totaling: ₹{total_budget:,.2f})")

# Helper Quick Shortcuts
st.markdown("##### Quick Split Options:")
shortcut_cols = st.columns(2)
with shortcut_cols[0]:
    if st.button("⚖️ Reset to Equal Distribution (20% Baseline)", use_container_width=True):
        for b in brands:
            st.session_state[f"alloc_{b}"] = 20
        st.rerun()
with shortcut_cols[1]:
    if st.button("📈 Skew towards Top Performing Brand", use_container_width=True):
        for b in brands:
            st.session_state[f"alloc_{b}"] = 50 if b == most_profitable_brand else 12.5
        st.rerun()

st.divider()

# ================================================================
# ALLOCATION SLIDERS
# ================================================================
st.markdown("### 🎛️ Step 2: Adjust Fund Splits")
slider_cols = st.columns(5)

total_allocated_pct = 0
for idx, b in enumerate(brands):
    with slider_cols[idx]:
        st.slider(f"{b} %", min_value=0, max_value=100, key=f"alloc_{b}")
        total_allocated_pct += st.session_state[f"alloc_{b}"]

# Real-time status tracker box
remaining_pct = 100 - total_allocated_pct
if total_allocated_pct == 100:
    st.markdown(f"<div style='background-color:rgba(40, 167, 69, 0.25); color:#28a745; padding:10px; border-radius:4px; text-align:center; font-weight:bold;'>✅ 100% Budget Distributed Perfectly</div>", unsafe_allow_html=True)
elif total_allocated_pct < 100:
    st.markdown(f"<div style='background-color:rgba(255, 193, 7, 0.2); color:#ffc107; padding:10px; border-radius:4px; text-align:center; font-weight:bold;'>⚠️ Under-allocated: {remaining_pct}% remaining to distribute.</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div style='background-color:rgba(220, 53, 69, 0.2); color:#dc3545; padding:10px; border-radius:4px; text-align:center; font-weight:bold;'>🔴 Over-allocated: Exceeded limit by {abs(remaining_pct)}%. Please reduce percentages.</div>", unsafe_allow_html=True)

st.divider()

# ================================================================
# COMPILATION & VISUALIZATION (GRAPHS & EXPECTED ROI)
# ================================================================
st.markdown("### 📊 Step 3: Allocation Analysis & Expected ROI Outcomes")

# Build data summary and projection matrix
allocation_data = []
for b in brands:
    pct = st.session_state[f"alloc_{b}"]
    allocated_amount = (pct / 100) * total_budget
    
    brand_data = brand_metrics[brand_metrics['Brand'] == b].iloc[0]
    roi_multiplier = brand_data['roi_score'] / 100
    expected_return = allocated_amount * roi_multiplier * (1 + brand_data['growth_30d']/100)
    
    expected_roi_pct = ((expected_return - allocated_amount) / max(allocated_amount, 1) * 100) if allocated_amount > 0 else 0
    
    allocation_data.append({
        'Brand': b,
        'Allocation %': pct,
        'Amount Allocated (₹)': allocated_amount,
        'Expected Return (₹)': expected_return,
        'Expected ROI %': expected_roi_pct
    })

allocation_df = pd.DataFrame(allocation_data)

# Summary table output helper
display_df = allocation_df.copy()
display_df['Allocation %'] = display_df['Allocation %'].apply(lambda x: f"{x}%")
display_df['Amount Allocated (₹)'] = display_df['Amount Allocated (₹)'].apply(lambda x: f"₹{x:,.2f}")
display_df['Expected Return (₹)'] = display_df['Expected Return (₹)'].apply(lambda x: f"₹{x:,.2f}")
display_df['Expected ROI %'] = display_df['Expected ROI %'].apply(lambda x: f"{x:+.1f}%")

st.dataframe(display_df, use_container_width=True, hide_index=True)

# Graph 1: Fund Allocation Pie/Donut Chart for All Brands
fig_allocation = px.pie(
    allocation_df,
    names='Brand',
    values='Amount Allocated (₹)',
    title="Fund Allocation Strategy Distribution across Brands",
    color_discrete_sequence=[COLORS['primary'], COLORS['accent_bright'], COLORS['success'], COLORS['warning'], COLORS['danger']]
)
fig_allocation.update_layout(height=350, font=dict(color=COLORS['white']))
st.plotly_chart(fig_allocation, use_container_width=True)

# Graph 2: Expected ROI Bar Chart per Brand
fig_roi = px.bar(
    allocation_df,
    x='Brand',
    y='Expected ROI %',
    color='Expected ROI %',
    color_continuous_scale=[COLORS['danger'], COLORS['warning'], COLORS['success']],
    title="Projected Brand-Wise Expected ROI %"
)
fig_roi.update_layout(height=300, font=dict(color=COLORS['white']))
st.plotly_chart(fig_roi, use_container_width=True)

# Overall totals scorecard block
total_invested = allocation_df['Amount Allocated (₹)'].sum()
total_returned = allocation_df['Expected Return (₹)'].sum()
portfolio_roi = ((total_returned - total_invested) / max(total_invested, 1) * 100) if total_invested > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Strategic Fund Deployed", f"₹{total_invested:,.2f}")
with col2:
    st.metric("Total Expected Gross Returns", f"₹{total_returned:,.2f}")
with col3:
    st.metric("Overall Aggregated ROI", f"{portfolio_roi:+.2f}%")

st.divider()

# ================================================================
# ACTIONS (SAVE / EXPORT)
# ================================================================
st.markdown("### 💾 Actions")
action_col1, action_col2 = st.columns(2)
with action_col1:
    if st.button("📥 Save Final Plan", use_container_width=True):
        st.session_state['fund_allocations'] = {b: st.session_state[f"alloc_{b}"] for b in brands}
        st.success("✅ Fund Allocation Plan successfully saved to memory!")

with action_col2:
    csv_export = pd.DataFrame(allocation_breakdown if 'allocation_breakdown' in locals() else allocation_data).to_csv(index=False)
    st.download_button(
        label="📊 Export Plan as CSV",
        data=csv_export,
        file_name=f"fund_allocation_inr_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )