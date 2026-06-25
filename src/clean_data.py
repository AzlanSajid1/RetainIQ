import pandas as pd
import os

def load_orders():
    df = pd.read_csv("data/processed/orders.csv")
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["customer_id"] = df["customer_id"].astype(str)
    df = df.dropna(subset=["customer_id", "total_price", "created_at"])
    return df

def load_customers():
    df = pd.read_csv("data/processed/customers.csv")
    df["customer_id"] = df["customer_id"].astype(str)
    return df

def get_summary(orders_df):
    print(f"Orders: {len(orders_df)}")
    print(f"Customers: {orders_df['customer_id'].nunique()}")
    print(f"Revenue: PKR {orders_df['total_price'].sum():,.0f}")
    print(f"Avg order value: PKR {orders_df['total_price'].mean():,.0f}")
    print(f"Date range: {orders_df['created_at'].min().date()} to {orders_df['created_at'].max().date()}")

if __name__ == "__main__":
    orders = load_orders()
    customers = load_customers()
    print("=== Data Summary ===")
    get_summary(orders)
    print("\nSample:")
    print(orders[["customer_id", "created_at", "total_price", "product_name"]].head(5))