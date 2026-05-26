"""
ITC PCPB MASTER CONTROL HUB
=====================================================
Main Multi-Page Router:
- Manages global layout styling and shared theme palettes
- Handles high-performance database caching 
- Routes users between the Control Room and the Planning Hub
"""

import streamlit as st
import pandas as pd
import sqlalchemy as sa
import urllib.parse
import os

# ================================================================
# GLOBAL DESIGN STYLE SETUP
# ================================================================
# Common color palette shared across pages
COLORS = {
    'primary': '#1479FF',
    'primary_light': 'rgba(20, 121, 255, 0.1)',
    'primary_medium': 'rgba(20, 121, 255, 0.3)',
    'dark_primary': '#195068',
    'darker': '#003868',
    'accent1': '#14D2FF',
    'accent2': '#14EBFF',
    'white': '#FFFFFF',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444'
}

st.set_page_config(
    page_title="ITC Business Planning & Tracking Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global dark glassmorphic styling safely to all pages
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
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
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
    color: {COLORS['white']} !important; font-weight: 600;
}}
p {{ color: {COLORS['white']} !important; }}
.stMetric {{
    background: rgba(255, 255, 255, 0.08) !important; backdrop-filter: blur(20px) !important;
    border-radius: 16px !important; border: 1px solid {COLORS['primary_medium']} !important;
    padding: 1.5rem !important;
}}
.analytics-box {{
    background: rgba(255, 255, 255, 0.08) !important; backdrop-filter: blur(20px) !important;
    border-radius: 20px !important; border: 1px solid {COLORS['primary_medium']} !important;
    padding: 2rem !important; margin: 1.5rem 0 !important; position: relative;
}}
.analytics-box::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent1']}, {COLORS['accent2']});
    border-radius: 20px 20px 0 0;
}}
</style>
""", unsafe_allow_html=True)

# ================================================================
# SHARED DATABASE CONNECTION LAYER
# ================================================================
@st.cache_resource
def init_shared_connection():
    try:
        DB_USER = "root"
        DB_PASSWORD = "siddhi@06"
        connection_string = f"mysql+pymysql://{DB_USER}:{urllib.parse.quote_plus(DB_PASSWORD)}@localhost/itc_sales_db"
        engine = sa.create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"❌ Shared Database Connection Error: {str(e)}")
        st.stop()

# Store engine in session state so sub-pages can grab it instantly
if 'db_engine' not in st.session_state:
    st.session_state['db_engine'] = init_shared_connection()

# ================================================================
# MULTI-PAGE ROUTER CONFIGURATION
# ================================================================
# Define your pages mapping directly to files
dashboard_page = st.Page("app.py", title="Master Sales Control Room", icon="🏢", default=True)
planning_page = st.Page("pages/planning_hub.py", title="Business Planning Hub", icon="🔮")

# Create navigation layout
pg = st.navigation([dashboard_page, planning_page])

# Run the navigation routing engine
pg.run()