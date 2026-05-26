"""
PCPB STRATEGIC PLANNING LAB (ADVANCED MODEL EDITION)
=====================================================
Upgraded Business Planning Sub-Page:
1. THE PREDICTOR - Powered by Holt-Winters Exponential Smoothing.
2. THE WARNING SYSTEM - Tracks 14-day safety buffers with Text-Based Stock Status Cards.
3. THE PRACTICE ROOM - Brand-Specific "What-If" Strategy Sliders.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import warnings
import numpy as np

# Import the advanced mathematical forecasting models
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Connect to the backend core logic
try:
    from kpi_logic import SalesKPIs
except ImportError:
    st.error("❌ Error: 'kpi_logic.py' file missing from main directory.")
    st.stop()

warnings.filterwarnings("ignore")

# Shared color tokens
COLORS = st.session_state.get('COLORS')

# Pull connection engine from the main router app memory
if 'db_engine' in st.session_state:
    engine = st.session_state['db_engine']
else:
    st.error("❌ Access Token Revoked: Run app.py directly to launch platform.")
    st.stop()

# Instead of running pd.read_sql again on subpages, just extract it instantly from memory
if 'raw_data' in st.session_state:
    df = st.session_state['raw_data']
else:
    st.error("Please start from the main dashboard.")
    st.stop()

# Sidebar regional filter constraint mapping
st.sidebar.markdown("### 🗺️ Hub Local Scope")
selected_regions = st.sidebar.multiselect(
    "Isolate Planning Regions", 
    options=sorted(df['Region'].dropna().unique()) if 'Region' in df.columns else [],
    default=sorted(df['Region'].dropna().unique()) if 'Region' in df.columns else []
)

filtered_df = df.copy()
if selected_regions and 'Region' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]

# Header Titles
st.markdown("<h1>ITC Business Planning Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.2rem; opacity: 0.9;'>A simple workspace to view upcoming brand targets, spot warehouse drops, and simulate pricing strategies risk-free to ensure better decision making.</p>", unsafe_allow_html=True)
st.markdown("---")

if not filtered_df.empty:
    
    # Get a clean list of available brands
    available_brands = sorted(filtered_df['Brand'].dropna().unique()) if 'Brand' in filtered_df.columns else []

    # ------------------------------------------------------------
    # SECTION 1: THE PREDICTOR (POWERED BY HOLT-WINTERS)
    # ------------------------------------------------------------
    st.markdown("## 🔮 1. The Predictor (Future Sales Targets)")
    st.markdown("<p>Select a specific brand and timeline to trigger the Holt-Winters predictive time-series algorithm.</p>", unsafe_allow_html=True)
    
    st.markdown('<div class="analytics-box">', unsafe_allow_html=True)
    control_col1, control_col2 = st.columns(2)
    with control_col1:
        chosen_brand = st.selectbox("🎯 Step 1: Select the Brand to Predict", options=available_brands, key="predictor_brand_select")
    with control_col2:
        forecast_months = st.slider("⏱️ Step 2: Select Future Prediction Range (Months)", min_value=1, max_value=6, value=1, step=1, key="predictor_months_slider")
    st.markdown('</div>', unsafe_allow_html=True)
    
    brand_df = filtered_df[filtered_df['Brand'] == chosen_brand] if 'Brand' in filtered_df.columns else filtered_df
    
    if not brand_df.empty:
        # Prepare the sales data timeline specifically for time-series modeling
        timeline_series = brand_df.groupby('Date')['Total Amount'].sum().asfreq('D', fill_value=0)
        current_brand_sales = brand_df['Total Amount'].sum()
        
        # Run Holt-Winters Exponential Smoothing
        try:
            # We use simple additive trends because the dataset spans one baseline calendar cycle
            hw_model = ExponentialSmoothing(timeline_series, trend='add', initialization_method="estimated").fit()
            # Predict the future days based on user selection (approx. 30 days per month)
            prediction_days = forecast_months * 30
            raw_forecast_array = hw_model.forecast(steps=prediction_days)
            total_future_prediction = max(0, float(raw_forecast_array.sum()))
        except Exception:
            # Safe business fallback to baseline mean if timeline steps are too narrow
            brand_brain_fallback = SalesKPIs(brand_df)
            total_future_prediction = brand_brain_fallback.get_forecast_revenue() * forecast_months

        col_pred1, col_pred2 = st.columns([1, 2])
        with col_pred1:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.metric(
                label=f"Advanced Forecast for {chosen_brand} (Next {forecast_months} Month{'s' if forecast_months > 1 else ''})",
                value=f"₹{total_future_prediction/1e6:.2f}M" if total_future_prediction >= 1e6 else f"₹{total_future_prediction/1e3:.1f}K"
            )
            st.caption("🤖 Model: Holt-Winters Smoothing. This tracks growth trend trajectories and weighs recent sales performance higher than older historical data rows.")
        with col_pred2:
            fig_pred = px.bar(
                x=[f'Current {chosen_brand} Sales Baseline', f'Holt-Winters Target ({forecast_months} Month Horizon)'], 
                y=[current_brand_sales, total_future_prediction],
                color=['Actuals', 'Prediction Target'],
                color_discrete_sequence=[COLORS['primary'], COLORS['accent2']]
            )
            fig_pred.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#fff'), showlegend=False, height=220, margin=dict(t=10,b=10))
            st.plotly_chart(fig_pred, use_container_width=True)
            
    st.markdown("---")
    
    # ------------------------------------------------------------
    # SECTION 2: THE WARNING SYSTEM & LIVE STOCK INSPECTOR
    # ------------------------------------------------------------
    st.markdown("## 🚨 2. The Warning System & Warehouse Stock Tracker")
    st.markdown("<p>Monitors warehouse quantity counts. View automatic low-stock alerts or look up the exact status of stock left for any category.</p>", unsafe_allow_html=True)
    
    total_days_tracked = (filtered_df['Date'].max() - filtered_df['Date'].min()).days
    if total_days_tracked <= 0:
        total_days_tracked = 1
        
    item_inventory = filtered_df.groupby(['Brand', 'Product Category']).agg(
        total_units_sold=('Quantity', 'sum'),
        current_stock=('Stock_Level', 'last')
    ).reset_index()
    
    item_inventory['Daily Sales Speed'] = item_inventory['total_units_sold'] / total_days_tracked
    item_inventory['14-Day Safety Buffer'] = np.ceil(item_inventory['Daily Sales Speed'] * 14)
    
    danger_items = item_inventory[item_inventory['current_stock'] < item_inventory['14-Day Safety Buffer']]
    
    st.markdown("### ⚠️ Automated Red Alerts")
    if not danger_items.empty:
        st.error(f"Red Alert: There are {len(danger_items)} segments running below safety buffers based on their current purchase velocities. Reorder soon!")
        
        display_danger_table = danger_items[['Brand', 'Product Category', 'Daily Sales Speed', '14-Day Safety Buffer', 'current_stock']].copy()
        display_danger_table['Daily Sales Speed'] = display_danger_table['Daily Sales Speed'].round(2)
        display_danger_table.columns = ['🏷️ Brand', '🧼 Segment', '📈 Daily Sales Speed', '🛡️ 14-Day Limit', '📦 Stock Left']
        
        st.dataframe(display_danger_table, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Supply Chain Healthy: All items have plenty of stock to cover the next 14 days of sales.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔍 Live Warehouse Stock Inspector")
    chosen_inspect_brand = st.selectbox("Select a Brand to look up its current warehouse count:", options=available_brands, key="stock_inspect_select")
    
    brand_stock_rows = item_inventory[item_inventory['Brand'] == chosen_inspect_brand]
    
    if not brand_stock_rows.empty:
        card_cols = st.columns(len(brand_stock_rows))
        for idx, (_, row) in enumerate(brand_stock_rows.iterrows()):
            category_name = row['Product Category']
            stock_left = int(row['current_stock'])
            safety_limit = int(row['14-Day Safety Buffer'])
            
            if stock_left < safety_limit:
                status_label = "⚠️ Shortage Risk"
                background_tint = "rgba(239, 68, 68, 0.15)"
                text_color = COLORS['danger']
            elif stock_left < (safety_limit * 1.5):
                status_label = "⚡ Stock Running Low"
                background_tint = "rgba(245, 158, 11, 0.15)"
                text_color = COLORS['warning']
            else:
                status_label = "✅ Fully Stocked"
                background_tint = "rgba(16, 185, 129, 0.15)"
                text_color = COLORS['success']
                
            with card_cols[idx]:
                st.markdown(f"""
                <div style='background: {background_tint}; border: 1px solid {text_color}; 
                            border-radius: 12px; padding: 1.2rem; text-align: center;'>
                    <p style='margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.8; font-weight: 600;'>{category_name}</p>
                    <h3 style='margin: 0 0 0.2rem 0; color: {COLORS["white"]}; font-size: 1.8rem;'>{stock_left:,} <span style='font-size: 1rem; opacity: 0.7;'>Units</span></h3>
                    <div style='color: {text_color}; font-size: 0.85rem; font-weight: 700; margin-top: 5px;'>{status_label}</div>
                    <p style='margin: 5px 0 0 0; font-size: 0.75rem; opacity: 0.6;'>14-Day Limit Buffer: {safety_limit} Units</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("No stock listings found for this specific view filter range.")

    st.markdown("---")
    
    # ------------------------------------------------------------
    # SECTION 3: THE PRACTICE ROOM (SCENARIO SIMULATOR)
    # ------------------------------------------------------------
    st.markdown("## 🎛️ 3. The Practice Room (Risk-Free Strategy Sandbox)")
    st.markdown("<p>Test out your business plans safely on screen before risking real company money. Select a brand below to run a test scenario.</p>", unsafe_allow_html=True)
    
    st.markdown('<div class="analytics-box">', unsafe_allow_html=True)
    sim_brand = st.selectbox("🎯 Target Brand to Simulate", options=available_brands, key="sandbox_brand_select")
    
    col_slide1, col_slide2 = st.columns(2)
    with col_slide1:
        price_change = st.slider(f"Adjust Retail Price for {sim_brand} (%)", -15, 25, 5, 5, key="sandbox_price_slider")
    with col_slide2:
        marketing_boost = st.slider(f"Adjust Marketing Budget for {sim_brand} (%)", -30, 100, 20, 10, key="sandbox_mkt_slider")
        
    sim_brand_df = filtered_df[filtered_df['Brand'] == sim_brand] if 'Brand' in filtered_df.columns else filtered_df
    
    if not sim_brand_df.empty:
        base_brand_revenue = sim_brand_df['Total Amount'].sum() if 'Total Amount' in sim_brand_df.columns else 0
        base_brand_units = sim_brand_df['Quantity'].sum() if 'Quantity' in sim_brand_df.columns else 0
        
        elasticity_impact = price_change * -1.4
        marketing_impact = marketing_boost * 0.4
        total_volume_shift = (elasticity_impact + marketing_impact) / 100.0
        
        simulated_revenue = base_brand_revenue * (1 + (price_change / 100.0)) * (1 + total_volume_shift)
        simulated_units = base_brand_units * (1 + total_volume_shift)
        
        st.markdown(f"### 📋 Predicted Results for {sim_brand} Under This Strategy:")
        col_res1, col_res2 = st.columns(2)
        col_res1.metric(
            label="Simulated Sales Revenue Result", 
            value=f"₹{simulated_revenue/1e6:.2f}M" if simulated_revenue >= 1e6 else f"₹{simulated_revenue/1e3:.1f}K", 
            delta=f"₹{(simulated_revenue - base_brand_revenue)/1e3:,.1f}K vs current brand base"
        )
        col_res2.metric(
            label="Simulated Total Item Volume Needed", 
            value=f"{simulated_units:,.0f} Pieces", 
            delta=f"{(simulated_units - base_brand_units):+,.0f} pieces from brand base"
        )
        
        fig_sim = px.bar(
            x=[f'Current Actual {sim_brand} Sales', f'Simulated {sim_brand} Performance'], 
            y=[base_brand_revenue, simulated_revenue],
            color=['Actual', 'Simulation'],
            color_discrete_sequence=[COLORS['primary'], COLORS['accent1']]
        )
        fig_sim.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#fff'), showlegend=False, height=220, margin=dict(t=10,b=10))
        st.plotly_chart(fig_sim, use_container_width=True)
    else:
        st.warning(f"No tracking logs available to simulate for brand: {sim_brand}")
        
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("⚠️ Notice: No data matches your current sidebar filters. Please choose wider filters to refresh the page charts.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.6; font-size: 0.85rem;'>ITC Personal Care Products Business (PCPB) Hub • Holt-Winters Production Deployment v4.0</p>", unsafe_allow_html=True)