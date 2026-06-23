# ITC InsightPulse – Interactive Sales Analytics & Intelligence Dashboard

ITC InsightPulse is a Business Intelligence (BI) and analytics platform developed for the *ITC Limited – Personal Care Products Business (PCPB) Division*.
The project combines **sales reporting, forecasting, inventory monitoring, and customer transaction simulation** into a single multi-page application using a **3-layer architecture (Frontend → API → Database)**.

## 📌 Features

*Executive Dashboard*
* Interactive sales analytics and KPI monitoring
* Revenue, order volume, and Average Order Value (AOV) tracking
* Dynamic filtering by brand, region, category, and time period
* Interactive charts and trend analysis

*Forecasting & Planning*
* Sales forecasting using historical data
* Scenario analysis for business planning
* Inventory monitoring with stock risk alerts

*Simulated Storefront*
* Simple storefront to simulate customer transactions
* Transaction flow connected to the analytics environment

*Backend Integration*
* API layer for communication between frontend and database
* Validation and structured data processing
* Modular architecture for scalability


## System Architecture

Storefront / Dashboard
         │
         ▼
   FastAPI Backend
         │
         ▼
   MySQL Database
   

## Project Structure:

```plaintext
├── app.py                    # Main application & navigation
├── api_server.py             # Backend API
├── preprocess.py             # Data preparation
└── pages/
    ├── Corporate_Dashboard.py
    ├── web_server.py
    ├── planning_hub.py
    ├── fund_allocator.py
    └── brand_correlation.py
```

## Tech Stack

**Frontend & UI**
* Streamlit
* HTML / CSS
  
**Backend**
* FastAPI
* Pydantic

**Database**
* MySQL
* SQLAlchemy

**Analytics & Forecasting**
* Pandas
* NumPy
* Statsmodels

**Visualization**
* Plotly


## Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/itc-insightpulse.git
cd itc-insightpulse
```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Configure Database
Create a MySQL database:
```sql
CREATE DATABASE itc_sales_db;
```
Update database credentials in the configuration files.
### 4. Run the Backend
```bash
python api_server.py
```
### 5. Launch the Dashboard
```bash
streamlit run app.py
```

## Project Goals
* Reduce manual reporting effort
* Improve access to business insights
* Support forecasting and planning
* Demonstrate scalable analytics architecture


Built as an internship project focused on **Business Intelligence, Sales Analytics, Forecasting, and Data-Driven Decision Support**.
