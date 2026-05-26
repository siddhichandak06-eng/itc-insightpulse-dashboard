import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import urllib.parse

# --- CONFIGURATION ---
DB_USER = "root"
DB_PASSWORD = "siddhi@06"
DB_NAME = "itc_sales_db"

# Updated file names
RAW_FILE = 'itc_pcpb_sales_2024_2025.csv'
OUTPUT_FILE = 'itc_pcpb_refined_sales_2024_2025.csv'

def extract_data(file_path):
    print("Extracting data...")
    return pd.read_csv(file_path)

def transform_data(df):
    print("Transforming data...")

    # 1. Cleaning
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)

    # Convert Date column
    df['Date'] = pd.to_datetime(df['Date'])

    # 2. Domain Mapping (ITC PCPB)
    category_map = {
        'Beauty': 'Personal Wash & Hygiene',
        'Clothing': 'Fragrances',
        'Electronics': 'Skincare & Haircare'
    }

    df['Product Category'] = df['Product Category'].map(category_map)

    # 3. Augmentation (Adding Industry Dimensions)
    itc_brands = ['Savlon', 'Fiama', 'Vivel', 'Engage', 'Dermafique']
    regions = ['North', 'South', 'East', 'West']
    distributors = [
        'ITC Hub Kolkata',
        'Northern Logistics',
        'Western Traders',
        'Southern Supply Co.'
    ]

    df['Brand'] = np.random.choice(itc_brands, size=len(df))
    df['Region'] = np.random.choice(regions, size=len(df))
    df['Distributor'] = np.random.choice(distributors, size=len(df))
    df['Stock_Level'] = np.random.randint(50, 500, size=len(df))

    return df


def load_data(df):
    print("Loading data to MySQL...")

    safe_password = urllib.parse.quote_plus(DB_PASSWORD)

    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{safe_password}@localhost/{DB_NAME}"
    )

    # Upload to MySQL
    df.to_sql('sales_data', con=engine, if_exists='replace', index=False)

    # Add constraints
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

    print("Load complete!")


if __name__ == "__main__":
    raw_df = extract_data(RAW_FILE)

    refined_df = transform_data(raw_df)

    load_data(refined_df)

    # Local backup
    refined_df.to_csv(OUTPUT_FILE, index=False)

    print("ETL Process Successful!")