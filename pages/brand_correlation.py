import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Shared global styles integration fallback check
COLORS = st.session_state.get('COLORS', {
    'primary': '#1479FF', 'primary_light': 'rgba(20, 121, 255, 0.1)',
    'primary_medium': 'rgba(20, 121, 255, 0.3)', 'accent1': '#14D2FF',
    'white': '#FFFFFF', 'danger': '#EF4444'
})

# Read unified filtering vectors from shared scope
df = st.session_state.get('filtered_data_view', st.session_state.get('raw_data'))

st.markdown("""
<div>
    <h1>🏷️ Brand Correlation Lab</h1>
    <p style='color: #14D2FF; margin-bottom: 1.5rem;'>Analyze sales relationships and product cannibalization metrics safely.</p>
</div>
""", unsafe_allow_html=True)

if df is not None and not df.empty:
    brand_col, date_col, amount_col = 'Brand', 'Date', 'Total Amount'
    
    if all(c in df.columns for c in [brand_col, date_col, amount_col]):
        time_frame = st.sidebar.selectbox("Aggregate Sales By:", options=["Daily", "Weekly", "Monthly"], index=2)
        resample_rule = 'D' if time_frame == "Daily" else 'W' if time_frame == "Weekly" else 'ME'

        # Process correlation matrices safely
        top_brands = df[brand_col].value_counts().nlargest(5).index.tolist()
        filtered_df = df[df[brand_col].isin(top_brands)]
        
        pivot_df = filtered_df.pivot_table(index=date_col, columns=brand_col, values=amount_col, aggfunc='sum').fillna(0)
        pivot_df.index = pd.to_datetime(pivot_df.index)
        pivot_resampled = pivot_df.resample(resample_rule).sum()
        corr_matrix = pivot_resampled.corr()

        custom_colorscale = [[0.0, COLORS['danger']], [0.5, '#0d1b2a'], [1.0, COLORS['accent1']]]
        
        fig_heatmap = px.imshow(
            corr_matrix, text_auto=".2f", aspect="auto",
            color_continuous_scale=custom_colorscale, zmin=-1.0, zmax=1.0
        )
        fig_heatmap.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['white'], family="Inter")
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # --- Strategic Observations Room ---
        st.markdown("### 🧠 Strategic Diagnostics")
        corr_upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        corr_stacked = corr_upper.unstack().dropna()
        
        if not corr_stacked.empty:
            col_obs1, col_obs2 = st.columns(2)
            with col_obs1:
                strongest_pos = corr_stacked.idxmax()
                st.success(f"📈 **Co-Movement**: {strongest_pos[0]} & {strongest_pos[1]} move in sync ({corr_stacked.max():.2f}).")
            with col_obs2:
                strongest_neg = corr_stacked.idxmin()
                if corr_stacked.min() < -0.1:
                    st.warning(f"⚠️ **Cannibalization Check**: {strongest_neg[0]} & {strongest_neg[1]} show inverse relationship ({corr_stacked.min():.2f}).")
                else:
                    st.info("✅ Minimal product sales line cannibalization detected across segments.")
else:
    st.error("❌ Sales tracking data not found. Please re-verify master workspace files.")