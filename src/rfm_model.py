import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.clean_data import load_orders

def run_rfm_model():
    orders = load_orders()
    today = orders["created_at"].max()

    # Build RFM manually
    rfm = orders.groupby("customer_id").agg(
        recency=("created_at", lambda x: (today - x.max()).days),
        frequency=("order_id", "count"),
        monetary=("total_price", "sum")
    ).reset_index()

    print("RFM sample:")
    print(rfm.head())

    # Scale features
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[["recency", "frequency", "monetary"]])

    # KMeans clustering
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm["cluster"] = km.fit_predict(rfm_scaled)

    # Label clusters by monetary value
    cluster_means = rfm.groupby("cluster")["monetary"].mean().sort_values(ascending=False)
    label_map = {
        cluster_means.index[0]: "Champions",
        cluster_means.index[1]: "Loyal",
        cluster_means.index[2]: "At Risk",
        cluster_means.index[3]: "Lost"
    }
    rfm["segment"] = rfm["cluster"].map(label_map)

    print("\n=== Segment Summary ===")
    summary = rfm.groupby("segment").agg(
        count=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean")
    ).round(1)
    print(summary)

    # Save
    rfm.to_csv("data/processed/rfm_results.csv", index=False)
    print("\nSaved to data/processed/rfm_results.csv")

    return rfm

if __name__ == "__main__":
    run_rfm_model()