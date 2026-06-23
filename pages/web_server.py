import streamlit as st
import requests
import random
from datetime import datetime

# Grab UI global styling variables or create a safe fallback
COLORS = st.session_state.get('COLORS', {
    'primary': '#1479FF', 'primary_light': 'rgba(20, 121, 255, 0.1)',
    'primary_medium': 'rgba(20, 121, 255, 0.3)', 'accent1': '#14D2FF',
    'accent2': '#14EBFF', 'white': '#FFFFFF', 'success': '#10B981', 'danger': '#EF4444'
})

# Embed custom CSS directly to maintain fluid application visuals
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{ background: linear-gradient(135deg, #000000 0%, #0a1f44 50%, #001f54 100%) fixed; }}
.analytics-box {{ 
    background: rgba(255, 255, 255, 0.06); border-radius: 16px; 
    border: 1px solid {COLORS['primary_medium']}; padding: 2rem; margin: 1.5rem 0; 
}}
h1 {{ font-family: 'Times New Roman', Times, serif !important; color: {COLORS['accent1']} !important; }}
p, label {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🌐 E-Commerce Web Portal Simulator</h1>", unsafe_allow_html=True)
st.markdown("<p style='opacity:0.75;'>Frontend Simulation Layer: Generate live consumer checkouts and push structured JSON frames through the middleware API.</p>", unsafe_allow_html=True)
st.markdown("---")

# Rigid Product Category Dictionary Matrix Lookup
portfolio_catalog = {
    'Fiama': [{'name': 'Fiama Gel Bar', 'cat': 'Soaps & Bars', 'price': 85.0},
              {'name': 'Fiama Shower Gel', 'cat': 'Shower Gels & Body Wash', 'price': 220.0}],
    'Vivel': [{'name': 'Vivel VedVidya Soap', 'cat': 'Soaps & Bars', 'price': 45.0},
              {'name': 'Vivel Fragrant Body Wash', 'cat': 'Shower Gels & Body Wash', 'price': 180.0}],
    'Engage': [{'name': 'Engage ON Pocket Perfume', 'cat': 'Pocket Perfumes', 'price': 65.0},
               {'name': 'Engage Deo Body Spray', 'cat': 'Deodorants', 'price': 210.0}],
    'Savlon': [{'name': 'Savlon Moisture Shield Handwash', 'cat': 'Handwash & Liquid Care', 'price': 99.0},
               {'name': 'Savlon Glycerin Soap', 'cat': 'Soaps & Bars', 'price': 55.0}],
    'Dermafique': [{'name': 'Dermafique Aqua Cloud Hydrating Crème', 'cat': 'Face Creams', 'price': 649.0},
                  {'name': 'Dermafique All Important Skin Toner', 'cat': 'Skin Toners', 'price': 399.0}]
}

st.markdown('<div class="analytics-box">', unsafe_allow_html=True)
st.markdown(f"<h3 style='color:{COLORS['accent2']}; margin-top:0;'>🛒 Interactive Operator Checkout Invoice</h3>", unsafe_allow_html=True)

# Layout Split Columns
col1, col2 = st.columns(2)

with col1:
    brand_selection = st.selectbox("1. Brand Portfolio Group:", list(portfolio_catalog.keys()))
    
    # Dynamically extract and assign variants matching ONLY the currently selected brand
    variants = portfolio_catalog[brand_selection]
    variant_names = [v['name'] for v in variants]
    
    product_selection = st.selectbox("2. Target Variation Variant:", variant_names)
    
    # Match information properties dynamically based on the active selection
    item_meta = next(v for v in variants if v['name'] == product_selection)
    calculated_unit_price = item_meta['price']
    category_assignment = item_meta['cat']
    
    order_quantity = st.number_input("3. Choose Volume Units:", min_value=1, max_value=250, value=5)
    
with col2:
    # FIXED: Sales Channel drop-down selector has been removed to match e-commerce containment properties.
    geographic_region = st.selectbox("4. Target Market Region:", ["North", "South", "East", "West", "NorthEast"])
    logistics_partner = st.text_input("5. Logistical Distributor Wholesaler:", value="ITC Distribution Hub Ltd")
    
    bill_subtotal = round(calculated_unit_price * order_quantity, 2)
    st.markdown(f"""
        <div style='margin-top:20px; padding:15px; background:{COLORS['primary_light']}; border:1px solid {COLORS['primary_medium']}; border-radius:8px; text-align:center;'>
            <span style='font-size:0.85rem; opacity:0.7;'>Live Computed Total:</span>
            <h2 style='margin:0; color:{COLORS['accent1']};'>₹{bill_subtotal:,.2f}</h2>
            <span style='font-size:0.75rem; opacity:0.6;'>({order_quantity} units × ₹{calculated_unit_price:.2f}/unit)</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Standard submission bridge action hook trigger
submit_button = st.button("🚀 Submit Invoice Order Package", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================================================================
# FRONT-END POST SUBMISSION LINK TO API ENGINE
# ================================================================
if submit_button:
    # Bundle data variables into a matching strict JSON packet payload
    packet_payload = {
        "Transaction_ID": random.randint(110000, 999999),
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Brand": brand_selection,
        "Product_Name": product_selection,
        "Product_Category": category_assignment,
        "Quantity": int(order_quantity),
        "Total_Amount": float(bill_subtotal),
        "Region": geographic_region,
        "Distributor": logistics_partner,
        "Channel": "E-Commerce",  # FIXED: Automated background data tag mapping assignment injection
        "Stock_Level": random.randint(300, 2500)
    }
    
    # Target address path of our independent FastAPI server bridge layer
    api_endpoint = "http://127.0.0.1:8000/api/v1/invoice"
    
    try:
        with st.spinner("Transmitting JSON telemetry packet across network layers..."):
            response = requests.post(api_endpoint, json=packet_payload, timeout=4)
            
        if response.status_code == 200:
            st.success(f"✅ Success (HTTP 200): Transaction added! Return message: {response.json().get('message')}")
            
            # Clears Streamlit cache arrays so dashboard displays updates instantly
            st.cache_data.clear()
            
            with st.expander("🔍 View Transmitted API JSON Payload"):
                st.json(packet_payload)
        else:
            st.error(f"🔴 API Flagged Error ({response.status_code}): {response.text}")
            
    except requests.exceptions.ConnectionError:
        st.markdown(f"""
            <div style='background:rgba(239, 68, 68, 0.15); border:1px solid {COLORS['danger']}; padding:15px; border-radius:10px;'>
                <h4 style='color:{COLORS['danger']}; margin:0;'>❌ Error: API Bridge Connection Refused!</h4>
                <p style='margin:5px 0 0 0; font-size:0.9rem;'>The front-end can't transmit the order because the backend middle layer is asleep. Run <code>python api_server.py</code> in a separate command line.</p>
            </div>
        """, unsafe_allow_html=True)