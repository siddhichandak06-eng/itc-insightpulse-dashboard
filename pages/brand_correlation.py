import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# 1. Grab the shared global color palette from Session State
if 'COLORS' in st.session_state:
    COLORS = st.session_state.COLORS
else:
    # Fallback default colors if run independently
    COLORS = {
        'primary': '#1479FF',
        'primary_light': 'rgba(20, 121, 255, 0.1)',
        'primary_medium': 'rgba(20, 121, 255, 0.3)',
        'accent1': '#14D2FF',
        'white': '#FFFFFF',
        'danger': '#EF4444'
    }

# 2. Safely extract raw data shared by app.py
if 'raw_data' in st.session_state and not st.session_state.raw_data.empty:
    df = st.session_state.raw_data.copy()
else:
    st.error("❌ No sales data found in memory. Please load the Master Control Room first.")
    st.stop()

# ================================================================
# PAGE HEADER
# ================================================================
st.markdown(f"""
<div>
    <h1 style='margin: 0;'>🏷️ Brand Correlation Lab</h1>
    <p style='color: {COLORS["accent1"]}; margin: 0.4rem 0 1.5rem 0; font-size: 1.1rem; font-weight: 500;'>
        Analyze sales relationships, market trends, and product cannibalization across ITC PCPB brands.
    </p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# DATA PREPARATION & PROCESSING
# ================================================================
# Ensure required columns exist (assuming 'Date', 'Brand', and 'Total Amount')
brand_col = 'Brand' 
date_col = 'Date'
amount_col = 'Total Amount'

if brand_col in df.columns and date_col in df.columns and amount_col in df.columns:
    
    # Let the user choose the time aggregation (Daily, Weekly, or Monthly)
    st.sidebar.markdown("### 🎛️ Analysis Settings")
    time_frame = st.sidebar.selectbox(
        "Aggregate Sales By:",
        options=["Daily", "Weekly", "Monthly"],
        index=2 # Default to Monthly for cleaner macro-trends
    )
    
    resample_rule = 'D' if time_frame == "Daily" else 'W' if time_frame == "Weekly" else 'ME'

    # Step 1: Pivot data so each brand has its own column of sales over time
    # This filters down to your primary top 5 brands dynamically
    top_5_brands = df[brand_col].value_counts().nlargest(5).index.tolist()
    filtered_df = df[df[brand_col].isin(top_5_brands)]
    
    pivot_df = filtered_df.pivot_table(
        index=date_col, 
        columns=brand_col, 
        values=amount_col, 
        aggfunc='sum'
    ).fillna(0)
    
    # Step 2: Resample based on user timeline choice to smooth out background noise
    pivot_resampled = pivot_df.resample(resample_rule).sum()
    
    # Step 3: Compute the Pearson Correlation Matrix (-1 to +1 scale)
    corr_matrix = pivot_resampled.corr()

    # ================================================================
    # VISUALIZATION: THE HEATMAP
    # ================================================================
    st.markdown(f"""
    <div class="analytics-box" style="background: rgba(255, 255, 255, 0.08); padding: 2rem; border-radius: 20px; border: 1px solid {COLORS['primary_medium']};">
        <h3 style='color: {COLORS["accent1"]}; margin: 0 0 1rem 0;'>Inter-Brand Sales Correlation Matrix</h3>
        <p style='color: {COLORS["white"]}; opacity: 0.8; font-size: 0.95rem;'>
            A value near <strong>+1</strong> means brands grow together. A value near <strong>-1</strong> indicates that when one brand sells well, the other drops (potential cannibalization).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Build custom diverging color scale matching your premium neon vibe
    # Diverging: Danger/Red for negative correlation, Dark for zero, Neon Blue/Cyan for positive
    custom_colorscale = [
        [0.0, COLORS['danger']],       # -1 Correlation
        [0.5, '#0d1b2a'],              # 0 Correlation (No relationship)
        [1.0, COLORS['accent1']]       # +1 Correlation
    ]
    
    fig_heatmap = px.imshow(
        corr_matrix,
        text_auto=".2f", # Displays correlation numbers cleanly rounded to 2 decimal places
        aspect="auto",
        labels=dict(x="Brand", y="Brand", color="Correlation Coefficient"),
        x=corr_matrix.columns,
        y=corr_matrix.index,
        color_continuous_scale=custom_colorscale,
        zmin=-1.0,
        zmax=1.0
    )
    
    # Update chart layouts to match your native dark-mode theme
    fig_heatmap.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['white'], family="Inter"),
        coloraxis_colorbar=dict(
            title="Correlation",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1.0 (Inverse)", "-0.5", "0.0 (None)", "0.5", "1.0 (Identical)"]
        )
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # ================================================================
    # EXECUTIVE INTERPRETATION CORNER
    # ================================================================
    st.markdown("---")
    st.markdown("### 🧠 Strategic Observations")
    
    # Programmatically find the strongest relationships to highlight to managers
    corr_upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    corr_stacked = corr_upper.unstack().dropna()
    
    col_obs1, col_obs2 = st.columns(2)
    
    with col_obs1:
        st.markdown(f"#### 📈 Strongest Co-Movement")
        strongest_pos = corr_stacked.idxmax()
        max_pos_val = corr_stacked.max()
        if max_pos_val > 0.4:
            st.success(f"**{strongest_pos[0]}** and **{strongest_pos[1]}** have the strongest positive relationship (**{max_pos_val:.2f}**). Their seasonal demand trends move highly in sync.")
        else:
            st.info("No exceptionally strong positive sales trends shared between independent brands in this timeframe.")
            
    with col_obs2:
        st.markdown(f"#### ⚠️ Cannibalization Risk Check")
        strongest_neg = corr_stacked.idxmin()
        min_neg_val = corr_stacked.min()
        if min_neg_val < -0.2:
            st.warning(f"**{strongest_neg[0]}** and **{strongest_neg[1]}** show an inverse correlation (**{min_neg_val:.2f}**). Watch out for marketing overlap or internal budget shifting eating into each other's market share.")
        else:
            st.info("Great news! Brands appear structurally independent. Minimal direct sales cannibalization detected.")

else:
    st.error("🚨 Column mismatch. Ensure your database fields contain 'Brand', 'Date', and 'Total Amount'.")