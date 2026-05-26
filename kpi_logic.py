import pandas as pd
import numpy as np


class SalesKPIs:

    def __init__(self, dataframe):

        # Create safe copy
        self.df = dataframe.copy()

        # Ensure Date column is datetime
        self.df['Date'] = pd.to_datetime(
            self.df['Date'],
            errors='coerce'
        )

        # Remove invalid dates
        self.df = self.df.dropna(subset=['Date'])

    # =====================================================
    # CORE SALES KPIs
    # =====================================================

    def get_total_revenue(self):
        """
        Total Revenue
        """
        return self.df['Total Amount'].sum()

    def get_average_transaction(self):
        """
        Average Order Value (AOV)
        """
        return self.df['Total Amount'].mean()

    def get_total_units(self):
        """
        Total Units Sold
        """
        return self.df['Quantity'].sum()

    def get_total_transactions(self):
        """
        Total Number of Transactions
        """
        return len(self.df)

    # =====================================================
    # ADVANCED KPIs
    # =====================================================

    def get_sku_velocity(self):
        """
        Units sold per brand per day
        """

        total_days = (
            self.df['Date'].max()
            - self.df['Date'].min()
        ).days

        if total_days <= 0:
            total_days = 1

        velocity = (
            self.df.groupby('Brand')['Quantity']
            .sum()
            / total_days
        )

        return velocity.sort_values(ascending=False)

    def get_regional_contribution(self):
        """
        Revenue contribution by region (%)
        """

        total = self.get_total_revenue()

        if total == 0:
            return pd.Series()

        regional_sums = (
            self.df.groupby('Region')['Total Amount']
            .sum()
        )

        contribution = (
            (regional_sums / total) * 100
        )

        return contribution.sort_values(ascending=False)

    def get_mom_growth(self):
        """
        Month-over-Month Growth %
        """

        monthly_sales = (
            self.df
            .set_index('Date')
            .resample('ME')['Total Amount']
            .sum()
        )

        if len(monthly_sales) < 2:
            return 0

        current_month = monthly_sales.iloc[-1]
        previous_month = monthly_sales.iloc[-2]

        if previous_month == 0:
            return 0

        growth = (
            (current_month - previous_month)
            / previous_month
        ) * 100

        return round(growth, 2)

    # =====================================================
    # INVENTORY KPIs
    # =====================================================

    def get_average_stock(self):
        """
        Average stock level
        """

        if 'Stock_Level' not in self.df.columns:
            return 0

        return self.df['Stock_Level'].mean()

    def get_low_stock_count(self, threshold=100):
        """
        Count products below stock threshold
        """

        if 'Stock_Level' not in self.df.columns:
            return 0

        return len(
            self.df[self.df['Stock_Level'] < threshold]
        )

    # =====================================================
    # SMART KPIs
    # =====================================================

    def get_sales_density(self):
        """
        Revenue per transaction
        """

        total_transactions = self.get_total_transactions()

        if total_transactions == 0:
            return 0

        return (
            self.get_total_revenue()
            / total_transactions
        )

    def get_top_brand(self):
        """
        Best performing brand
        """

        if self.df.empty:
            return "N/A"

        return (
            self.df.groupby('Brand')['Total Amount']
            .sum()
            .idxmax()
        )

    def get_top_region(self):
        """
        Best performing region
        """

        if self.df.empty:
            return "N/A"

        return (
            self.df.groupby('Region')['Total Amount']
            .sum()
            .idxmax()
        )

    def get_forecast_revenue(self):
        """
        Simple Moving Average Forecast
        """

        monthly_sales = (
            self.df
            .set_index('Date')
            .resample('ME')['Total Amount']
            .sum()
        )

        if len(monthly_sales) == 0:
            return 0

        if len(monthly_sales) < 3:
            return monthly_sales.mean()

        return monthly_sales.tail(3).mean()