"""
preprocess.py
===================================================================
Handles core database connections and data cleansing for ITC InsightPulse.
Upgraded to fetch permanent database columns (Product Name, Product Category, 
Stock_Level, Channel) directly from the newly migrated MySQL schema.
"""

import os
import urllib.parse
import pandas as pd
import sqlalchemy as sa
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def init_connection():
    """Initialize database connection safely"""
    try:
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "siddhi@06")  
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


@st.cache_data(ttl=300)
def get_processed_data():
    """Loads and prepares the permanently enriched dataset directly from MySQL"""
    try:
        engine = init_connection()
        # Fetching rows directly from your permanently updated dataset schema
        query = "SELECT * FROM sales_data LIMIT 100000"
        df = pd.read_sql(query, engine)
        engine.dispose()
        
        # --- Data Cleaning ---
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
        
        numeric_cols = ['Quantity', 'Total Amount', 'Stock_Level']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        
        if 'Total Amount' in df.columns and 'Quantity' in df.columns:
            df = df[(df['Total Amount'] >= 0) & (df['Quantity'] >= 0)]
            
        # Standardize space-separated names to match existing dashboard visual references
        if 'Product_Name' in df.columns:
            df.rename(columns={'Product_Name': 'Product Name'}, inplace=True)
        if 'Product_Category' in df.columns:
            df.rename(columns={'Product_Category': 'Product Category'}, inplace=True)

        return df.sort_values('Date') if 'Date' in df.columns else df
        
    except Exception as e:
        st.error(f"❌ Preprocessing Data Error: {str(e)}")
        st.stop()