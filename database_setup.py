import pandas as pd
from sqlalchemy import create_engine, text
import mysql.connector
import urllib.parse

# --- CONFIGURATION ---
DB_USER = "root"
DB_PASSWORD = "siddhi@06"
DB_HOST = "localhost"
DB_NAME = "itc_sales_db"
TABLE_NAME = "sales_data"

# Updated CSV file name
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

        # 2. Read cleaned CSV data
        print(f"Reading {CSV_FILE}...")
        df = pd.read_csv(CSV_FILE)
        # Convert Date column
        df['Date'] = pd.to_datetime(df['Date'])

        # 3. Encode password safely
        safe_password = urllib.parse.quote_plus(DB_PASSWORD)

        # 4. Create SQLAlchemy Engine
        engine = create_engine(
            f"mysql+pymysql://{DB_USER}:{safe_password}@{DB_HOST}/{DB_NAME}"
        )

        # 5. Upload data to MySQL
        print("Uploading data to MySQL...")
        df.to_sql(
            TABLE_NAME,
            con=engine,
            if_exists='replace',
            index=False
        )

        # 6. Add Primary Key Constraint
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

        print("Successfully uploaded all records to MySQL!")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    setup_database()