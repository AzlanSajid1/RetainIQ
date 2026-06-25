import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

FIRST_NAMES = ["Ali","Sara","Usman","Ayesha","Hassan","Fatima","Ahmed","Zara","Omar","Hina","Bilal","Sana","Tariq","Nadia","Kamran","Imran","Rabia","Shahid","Amna","Faisal"]
LAST_NAMES = ["Khan","Ahmed","Ali","Hassan","Sheikh","Malik","Qureshi","Akhtar","Chaudhry","Mirza"]
PRODUCTS = [
    {"name": "Wireless Earbuds Pro", "price": 4999},
    {"name": "Smart Watch Series X", "price": 12999},
    {"name": "Laptop Stand Adjustable", "price": 2499},
    {"name": "USB-C Hub 7-in-1", "price": 3499},
    {"name": "Mechanical Keyboard", "price": 8999},
    {"name": "Webcam HD 1080p", "price": 5999},
    {"name": "Phone Case Premium", "price": 999},
    {"name": "Screen Protector Pack", "price": 499},
]

# Generate 300 customers with different behaviors
NUM_CUSTOMERS = 300
customers = []
for i in range(NUM_CUSTOMERS):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    customers.append({
        "customer_id": f"CUST{1000+i}",
        "email": f"{first.lower()}.{last.lower()}{i}@email.com",
        "first_name": first,
        "last_name": last,
        # behavior type determines how active this customer is
        "behavior": random.choices(
            ["champion", "loyal", "at_risk", "lost"],
            weights=[15, 25, 35, 25]
        )[0]
    })

# Generate orders based on customer behavior
orders = []
order_id = 10000
today = datetime.now()

for customer in customers:
    behavior = customer["behavior"]

    if behavior == "champion":
        # Bought many times, recently
        num_orders = random.randint(8, 15)
        max_days_ago = 30
    elif behavior == "loyal":
        # Bought several times, fairly recently
        num_orders = random.randint(4, 8)
        max_days_ago = 90
    elif behavior == "at_risk":
        # Used to buy, hasn't in a while
        num_orders = random.randint(2, 5)
        max_days_ago = 365
    else:  # lost
        # Bought once or twice, long ago
        num_orders = random.randint(1, 2)
        max_days_ago = 365

    # Space out their orders over time
    for j in range(num_orders):
        if behavior == "champion":
            days_ago = random.randint(1, max_days_ago)
        elif behavior == "loyal":
            days_ago = random.randint(10, max_days_ago)
        elif behavior == "at_risk":
            days_ago = random.randint(120, max_days_ago)
        else:
            days_ago = random.randint(200, max_days_ago)

        order_date = today - timedelta(days=days_ago)
        product = random.choice(PRODUCTS)
        quantity = random.randint(1, 3)
        total = product["price"] * quantity

        orders.append({
            "order_id": f"ORD{order_id}",
            "customer_id": customer["customer_id"],
            "email": customer["email"],
            "first_name": customer["first_name"],
            "last_name": customer["last_name"],
            "created_at": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "total_price": total,
            "product_name": product["name"],
            "quantity": quantity,
            "financial_status": "paid"
        })
        order_id += 1

# Save to CSV
os.makedirs("data/processed", exist_ok=True)
orders_df = pd.DataFrame(orders)
orders_df = orders_df.sort_values("created_at").reset_index(drop=True)
orders_df.to_csv("data/processed/orders.csv", index=False)

customers_df = pd.DataFrame(customers)
customers_df.to_csv("data/processed/customers.csv", index=False)

print(f"Generated {len(orders_df)} orders for {len(customers_df)} customers")
print(f"Date range: {orders_df['created_at'].min()} to {orders_df['created_at'].max()}")
print(f"\nCustomer breakdown:")
print(customers_df['behavior'].value_counts())
print(f"\nSaved to data/processed/")
