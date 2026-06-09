import pandas as pd
from sqlalchemy import create_engine, text
import mysql.connector
import urllib.parse
import numpy as np

# --- CONFIGURATION ---
DB_USER = "root"
DB_PASSWORD = ""  # FIXED: Set to empty for XAMPP
DB_HOST = "localhost"
DB_NAME = "itc_sales_db"
TABLE_NAME = "sales_data"
CSV_FILE = "itc_pcpb_refined_sales.csv"

def setup_database():
    try:
        # 1. Connect to MySQL Server and create database if needed
        print("Connecting to MySQL Server...")
        temp_conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = temp_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"Database '{DB_NAME}' is ready.")
        temp_conn.close()

        # 2. Read original CSV data
        print(f"Reading {CSV_FILE}...")
        df = pd.read_csv(CSV_FILE)
        
        # Clean up column parameters
        df['Date'] = pd.to_datetime(df['Date'])
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(1)
        df['Total Amount'] = pd.to_numeric(df['Total Amount'], errors='coerce').fillna(0)

        # ================================================================
        # HIGH-PERFORMANCE FEATURE INTEGRATION (UPDATING THE TABLE DATA)
        # ================================================================
        print("⚙️ Enhancing dataset with product profiles and sales channels...")
        np.random.seed(101)
        
        # Setup the standard FMCG product catalog matching your preprocessor logic
        variant_catalog = {
            'Fiama': [
                {'name': 'Fiama Gel Bar', 'cat': 'Soaps & Bars', 'price_weight': 1.0, 'vol_weight': 1.4},
                {'name': 'Fiama Shower Gel', 'cat': 'Shower Gels & Body Wash', 'price_weight': 2.8, 'vol_weight': 0.8}
            ],
            'Vivel': [
                {'name': 'Vivel VedVidya Soap', 'cat': 'Soaps & Bars', 'price_weight': 0.8, 'vol_weight': 1.6},
                {'name': 'Vivel Fragrant Body Wash', 'cat': 'Shower Gels & Body Wash', 'price_weight': 2.4, 'vol_weight': 0.7}
            ],
            'Engage': [
                {'name': 'Engage ON Pocket Perfume', 'cat': 'Pocket Perfumes', 'price_weight': 1.2, 'vol_weight': 1.3},
                {'name': 'Engage Deo Body Spray', 'cat': 'Deodorants', 'price_weight': 2.2, 'vol_weight': 0.9}
            ],
            'Savlon': [
                {'name': 'Savlon Moisture Shield Handwash', 'cat': 'Handwash & Liquid Care', 'price_weight': 1.5, 'vol_weight': 1.2},
                {'name': 'Savlon Antiseptic Disinfectant Liquid', 'cat': 'Antiseptics', 'price_weight': 2.5, 'vol_weight': 0.8},
                {'name': 'Savlon Glycerin Soap', 'cat': 'Soaps & Bars', 'price_weight': 0.9, 'vol_weight': 1.4}
            ],
            'Dermafique': [
                {'name': 'Dermafique Aqua Cloud Hydrating Crème', 'cat': 'Face Creams', 'price_weight': 5.5, 'vol_weight': 0.4},
                {'name': 'Dermafique All Important Skin Toner', 'cat': 'Skin Toners', 'price_weight': 4.2, 'vol_weight': 0.6}
            ]
        }

        # Allocate clean arrays for fast computation loop
        names_array = np.empty(len(df), dtype=object)
        cats_array = np.empty(len(df), dtype=object)
        
        brands = df['Brand'].values.copy()
        quantities = df['Quantity'].values.copy()
        amounts = df['Total Amount'].values.copy()

        # Fill text variants and compute scaled sales figures smoothly
        for idx in range(len(df)):
            brand = brands[idx]
            if brand in variant_catalog:
                variants = variant_catalog[brand]
                selected_variant_idx = idx % len(variants)
                v_meta = variants[selected_variant_idx]
                
                names_array[idx] = v_meta['name']
                cats_array[idx] = v_meta['cat']
                
                # Apply balanced random marketplace fluctuations
                noise = np.random.uniform(0.9, 1.15)
                quantities[idx] = max(1, int(quantities[idx] * v_meta['vol_weight'] * noise))
                amounts[idx] = round(amounts[idx] * v_meta['price_weight'] * noise, 2)
            else:
                names_array[idx] = f"{brand} Generic Variant"
                cats_array[idx] = "Personal Care"

        # Apply newly created arrays directly as brand-new permanent database columns
        df['Product Name'] = names_array
        df['Product Category'] = cats_array
        df['Quantity'] = quantities
        df['Total Amount'] = amounts
        
        # Add random warehouse stock level entries between 500 and 3000 units
        df['Stock_Level'] = np.random.randint(500, 3000, size=len(df))
        
        # Add the multi-channel criteria from your channel performance feedback
        distribution_channels = [
            "E-Commerce (Amazon)", 
            "Merchandising (Shoppers Stop)", 
            "Retailer (Traditional Trade)"
        ]
        # Distribute rows realistically: 40% Online E-Comm, 30% Modern trade, 30% Retail shops
        df['Channel'] = np.random.choice(distribution_channels, size=len(df), p=[0.40, 0.30, 0.30])

        # ================================================================
        # DATABASE UPLOAD CONSTRAINTS
        # ================================================================
        # 3. Encode password safely
        safe_password = urllib.parse.quote_plus(DB_PASSWORD)

        # 4. Create SQLAlchemy Engine
        engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{safe_password}@{DB_HOST}/{DB_NAME}"
        )

        # 5. Upload completely enriched dataframe to MySQL
        print("💾 Uploading complete dataset with all new features to MySQL...")
        df.to_sql(
            TABLE_NAME,
            con=engine,
            if_exists='replace',
            index=False
        )

        # 6. Re-apply Key Constraints to secure indices
        print("🔑 Re-applying Database Keys & Constraints...")
        with engine.connect() as con:
            con.execute(
                text("""
                    ALTER TABLE sales_data
                    MODIFY COLUMN `Transaction ID` INT NOT NULL;
                """)
            )
            con.execute(
                text("""
                    ALTER TABLE sales_data
                    ADD PRIMARY KEY (`Transaction ID`);
                """)
            )
            con.commit()

        print("🎉 Success! Your MySQL database table has been completely updated with Product Names, Categories, Stock Levels, and Channels!")

    except Exception as e:
        print(f"❌ Error occurred during database setup: {e}")

if __name__ == "__main__":
    setup_database()