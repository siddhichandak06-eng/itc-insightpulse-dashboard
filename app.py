import streamlit as st
import os

# Set up global page layout properties
st.set_page_config(page_title="ITC Portal Gateway", layout="wide")

# Premium UI Styling Theme
COLORS = {
    'primary': '#1479FF', 'primary_light': 'rgba(20, 121, 255, 0.1)',
    'primary_medium': 'rgba(20, 121, 255, 0.3)', 'dark_primary': '#195068',
    'dark_secondary': '#161616', 'darker': '#003868', 'accent1': '#14D2FF',
    'accent2': '#14EBFF', 'accent_bright': '#00D9FF', 'accent_warm': '#FFB81C',
    'white': '#FFFFFF', 'success': '#10B981', 'warning': '#F59E0B', 'danger': '#EF4444'
}
st.session_state.COLORS = COLORS

# Initialize Session State variables for authentication tracking
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ================================================================
# 🔑 LOGIN GATED VIEW FUNCTION
# ================================================================
def render_login_gateway():
    st.markdown(f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{ background: linear-gradient(135deg, #000000 0%, #0a1f44 50%, #001f54 100%) fixed; }}
    .gateway-box {{
        background: rgba(255, 255, 255, 0.05); border-radius: 16px;
        border: 1px solid {COLORS['primary_medium']}; padding: 2.5rem; text-align: center;
    }}
    h1 {{ font-family: 'Times New Roman', Times, serif !important; color: {COLORS['accent1']} !important; text-align: center; font-size: 3rem !important; }}
    p, label {{ color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>🏢 ITC Limited Enterprise Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity:0.8;'>Welcome to the Personal Care Products Business (PCPB) Hub. Please select your role to proceed.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Layout splitting for clear dual-role options
    col1, space, col2 = st.columns([2, 0.5, 2])

    with col1:
        st.markdown('<div class="gateway-box">', unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:{COLORS['accent2']}; margin-top:0;'>🛒 Consumer Storefront</h2>", unsafe_allow_html=True)
        st.markdown("<p style='height: 60px;'>Browse the ITC product portfolio catalog, customize variants, and place retail orders directly.</p>", unsafe_allow_html=True)
        if st.button("Launch E-Commerce Portal", use_container_width=True, type="primary"):
            st.switch_page("pages/web_server.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="gateway-box">', unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:{COLORS['accent2']}; margin-top:0;'>📊 Corporate Management</h2>", unsafe_allow_html=True)
        st.markdown("<p style='height: 60px;'>Access corporate BI tools, regional performance charts, supply trackers, and master administrative controls.</p>", unsafe_allow_html=True)
        
        # Expand secure login form directly inside the column block
        with st.expander("🔑 Secure Employee Login", expanded=True):
            user_id = st.text_input("User ID:")
            password = st.text_input("Password:", type="password")
            
            if st.button("Authenticate & Enter", use_container_width=True):
                if user_id == "itcadmin" and password == "pcpb2026":
                    st.session_state.authenticated = True
                    st.success("Access Granted!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. Access Denied.")
        st.markdown('</div>', unsafe_allow_html=True)

# ================================================================
# 🗺️ CENTRAL NATIVE NAVIGATION ROUTER
# ================================================================
# Step 1: Define Pages
login_gateway_page = st.Page(render_login_gateway, title="Portal Login Gateway", icon="🔒")
web_server_portal = st.Page("pages/web_server.py", title="E-Commerce Storefront", icon="🛒")

# FIXED: Added default=True parameter to land directly inside the Corporate Control room upon login
main_dashboard = st.Page("pages/Corporate_Dashboard.py", title="Master Sales Control Room", icon="🏢", default=True)
planning_hub = st.Page("pages/planning_hub.py", title="Business Planning Hub", icon="🔮")
fund_allocator = st.Page("pages/fund_allocator.py", title="Strategic Fund Allocator", icon="💰")
brand_correlation = st.Page("pages/brand_correlation.py", title="Brand Correlation", icon="🏷️")

# Step 2: Dynamically Scan Sub-pages safely
brand_diagnostic_pages = []
if os.path.exists("pages"):
    for file in sorted(os.listdir("pages")):
        if file.endswith(".py") and file not in ["planning_hub.py", "fund_allocator.py", "brand_correlation.py", "web_server.py", "Corporate_Dashboard.py"]:
            brand_diagnostic_pages.append(st.Page(f"pages/{file}", title=file.replace(".py", "").replace("_", " ").title(), icon="🏷️"))

# Step 3: Enforce Authentication Visibility Hierarchy
if not st.session_state.authenticated:
    # Public Layer: Hide everything except login page and e-comm storefront
    navigation_ecosystem = st.navigation({
        "Gateway Authorization": [login_gateway_page],
        "Public Client View": [web_server_portal]
    })
else:
    # Corporate Layer: Unlock full admin menu suites securely
    # FIXED: Reordered layout dictionary entries so Executive Control Room lands first in the sidebar structure
    navigation_ecosystem = st.navigation({
        "Executive Control Room": [main_dashboard],
        "Front End User Portal": [web_server_portal],
        "Strategic Analysis Labs": [planning_hub, fund_allocator, brand_correlation],
        "Brand Diagnostics Suite": brand_diagnostic_pages
    })

navigation_ecosystem.run()