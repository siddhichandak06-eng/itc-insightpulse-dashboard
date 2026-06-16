from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlalchemy as sa
import uvicorn
import os

app = FastAPI(
    title="ITC InsightPulse Web API Gateway",
    description="Secure 3-Layer Middleware Engine connecting front-end simulators to MySQL storage layers."
)

# ================================================================
# DATABASE NATIVE CONNECTION CONFIGURATION
# ================================================================
DB_USER = "root"
DB_PASSWORD = ""      # Blank for XAMPP default
DB_HOST = "localhost"  # Default active port 3306
DB_NAME = "itc_sales_db"

# Create a clean SQL injection resistant engine connection pipeline
connection_url = f"mysql+pymysql://{DB_USER}@{DB_HOST}/{DB_NAME}"
engine = sa.create_engine(connection_url)

# ================================================================
# DATA SCHEMA CORRELATION LAYER (Pydantic)
# ================================================================
# Enforces strict data types on incoming JSON payloads before allowing database entry
class TransactionSchema(BaseModel):
    Transaction_ID: int
    Date: str
    Brand: str
    Product_Name: str
    Product_Category: str
    Quantity: int
    Total_Amount: float
    Region: str
    Distributor: str
    Channel: str
    Stock_Level: int

# ================================================================
# API ROUTE ROUTERS
# ================================================================
@app.post("/api/v1/invoice", status_code=200)
def process_storefront_invoice(payload: TransactionSchema):
    """
    Receives incoming JSON checkout payloads from the E-comm portal, Evaluates parameters, 
    and issues a secure structural insert query straight down to the underlying MySQL engine.
    """
    try:
        with engine.begin() as conn:
            # Construct a parameterized SQL string to ensure maximum protection against data injection
            raw_query = sa.text("""
                INSERT INTO sales_data 
                (`Transaction ID`, Date, Brand, `Product Name`, `Product Category`, Quantity, `Total Amount`, Region, Distributor, Channel, Stock_Level)
                VALUES (:tid, :date, :brand, :pname, :pcat, :qty, :amt, :region, :dist, :channel, :stock)
            """)
            
            # Unpack the payload directly into the query execution string
            conn.execute(raw_query, {
                "tid": payload.Transaction_ID,
                "date": payload.Date,
                "brand": payload.Brand,
                "pname": payload.Product_Name,
                "pcat": payload.Product_Category,
                "qty": payload.Quantity,
                "amt": payload.Total_Amount,
                "region": payload.Region,
                "dist": payload.Distributor,
                "channel": payload.Channel,
                "stock": payload.Stock_Level
            })
            
        return {
            "status": "Success",
            "message": "Transaction written smoothly into MySQL database row arrays!"
        }
    except Exception as e:
        # Catch errors securely and return an internal server error status
        raise HTTPException(status_code=500, detail=f"Database Write Failure: {str(e)}")

if __name__ == "__main__":
    # Launch Uvicorn local host loop when called from shell terminal command
    uvicorn.run(app, host="127.0.0.1", port=8000)