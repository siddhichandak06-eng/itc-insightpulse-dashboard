"""
preprocess.py
===================================================================
Handles core database connections, data cleansing, and structural
feature engineering (PCPB product mapping) for ITC InsightPulse.
"""

import os
import urllib.parse
import numpy as np
import pandas as pd
import sqlalchemy as sa
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def init_connection():
    """Initialize database connection safely"""
    try:
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")  
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_NAME = os.getenv("DB_NAME", "itc_sales_db")

        connection_string = f"mysql+pymysql://{DB_USER}:{urllib.parse.quote_plus(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}"
        engine = sa.create_engine(connection_string)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        return engine
    except Exception as e:
        st.error(f"❌ Database Connection Error: {str(e)}")
        st.stop()


@st.cache_data(ttl=300)
def get_processed_data():
    """Loads, cleans, and applies specific real-world ITC PCPB product mappings"""
    try:
        engine = init_connection()
        query = "SELECT * FROM sales_data LIMIT 100000"
        df = pd.read_sql(query, engine)
        engine.dispose()
        
        # --- Data Cleaning ---
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
        
        numeric_cols = ['Quantity', 'Total Amount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        
        if 'Total Amount' in df.columns and 'Quantity' in df.columns:
            df = df[(df['Total Amount'] >= 0) & (df['Quantity'] >= 0)]
            
        # --- Strict Real-World ITC PCPB Product Mapping ---
        if 'Brand' in df.columns and 'Product Category' in df.columns:
            conditions = [
                # 1. Fiama Mappings
                (df['Brand'] == 'Fiama') & (df['Product Category'].str.contains('Soap|Bar', case=False, na=False)),
                (df['Brand'] == 'Fiama') & (df['Product Category'].str.contains('Gel|Shower|Wash|Hygiene', case=False, na=False)),
                
                # 2. Vivel Mappings
                (df['Brand'] == 'Vivel') & (df['Product Category'].str.contains('Soap|Bar', case=False, na=False)),
                (df['Brand'] == 'Vivel') & (df['Product Category'].str.contains('Wash|Body', case=False, na=False)),
                
                # 3. Engage Mappings (Catches 'Fragrances', 'Deo', 'Perfume')
                (df['Brand'] == 'Engage') & (df['Product Category'].str.contains('Pocket|ON|Perfume|EDP', case=False, na=False)),
                (df['Brand'] == 'Engage') & (df['Product Category'].str.contains('Deo|Spray|Body|Fragrance', case=False, na=False)),
                
                # 4. Savlon Mappings (Catches 'Personal Wash & Hygiene', 'Handwash')
                (df['Brand'] == 'Savlon') & (df['Product Category'].str.contains('Handwash|Liquid Hand|Wash|Hygiene', case=False, na=False)),
                (df['Brand'] == 'Savlon') & (df['Product Category'].str.contains('Antiseptic|Disinfectant', case=False, na=False)),
                (df['Brand'] == 'Savlon') & (df['Product Category'].str.contains('Soap|Bar', case=False, na=False)),
                
                # 5. Dermafique Mappings
                (df['Brand'] == 'Dermafique') & (df['Product Category'].str.contains('Cream|Crème|Moisturizer', case=False, na=False)),
                (df['Brand'] == 'Dermafique') & (df['Product Category'].str.contains('Toner|Serum|Cleanser', case=False, na=False))
            ]
            
            choices = [
                'Fiama Gel Bar',
                'Fiama Shower Gel',
                
                'Vivel VedVidya Soap',
                'Vivel Fragrant Body Wash',
                
                'Engage ON Pocket Perfume',
                'Engage Deo Body Spray',
                
                'Savlon Moisture Shield Handwash',
                'Savlon Antiseptic Disinfectant Liquid',
                'Savlon Glycerin Soap',
                
                'Dermafique Aqua Cloud Hydrating Crème',
                'Dermafique All Important Skin Toner'
            ]
            
            # Apply mappings; clean up fallback default names cleanly if pattern fails
            df['Product Name'] = np.select(conditions, choices, default=df['Brand'] + " " + df['Product Category'])
            
            # Global string cleaners to patch unexpected fallbacks like "Savlon Personal Wash & Hygiene"
            df['Product Name'] = df['Product Name'].str.replace('Personal Wash & Hygiene', 'Moisture Shield Handwash', case=False)
            df['Product Name'] = df['Product Name'].str.replace('Fragrances', 'Deo Body Spray', case=False)
            
        else:
            df['Product Name'] = "ITC Personal Care Product"
            
        return df.sort_values('Date') if 'Date' in df.columns else df
        
    except Exception as e:
        st.error(f"❌ Preprocessing Data Error: {str(e)}")
        st.stop()