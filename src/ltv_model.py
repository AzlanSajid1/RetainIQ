import pandas as pd
import numpy as np
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.clean_data import load_orders

def run_ltv_model():
    orders = load_orders()
    today = orders["created_at"].max()

    # Build RFM summary — lifetimes needs this specific format
    rfm = summary_data_from_transaction_data(
        orders,
        customer_id_col="customer_id",
        datetime_col="created_at",
        monetary_value_col="total_price",
        observation_period_end=today,
        freq="D"
    )

    print(f"RFM table built for {len(rfm)} customers")
    print(rfm.head())

    # Fit BG/NBD model
    print("\nFitting BG/NBD model...")
    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(rfm["frequency"], rfm["recency"], rfm["T"])
    print("BG/NBD model fitted.")

    # Predict purchases in next 30 days
    rfm["predicted_purchases_30d"] = bgf.conditional_expected_number_of_purchases_up_to_time(
        30, rfm["frequency"], rfm["recency"], rfm["T"]
    )

    # Churn flag — customers unlikely to buy in next 30 days
    rfm["churn_risk"] = rfm["predicted_purchases_30d"].apply(
        lambda x: "High Risk" if x < 0.3 else ("Medium Risk" if x < 0.6 else "Low Risk")
    )

    # Gamma-Gamma for CLV (only customers with repeat purchases)
    print("\nFitting Gamma-Gamma model...")
    rfm_repeat = rfm[rfm["frequency"] > 0]
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(rfm_repeat["frequency"], rfm_repeat["monetary_value"])

    rfm["predicted_clv_12m"] = ggf.customer_lifetime_value(
        bgf,
        rfm["frequency"],
        rfm["recency"],
        rfm["T"],
        rfm["monetary_value"],
        time=12,
        freq="D"
    )

    print("\n=== Results ===")
    print(f"High Risk customers: {(rfm['churn_risk'] == 'High Risk').sum()}")
    print(f"Medium Risk customers: {(rfm['churn_risk'] == 'Medium Risk').sum()}")
    print(f"Low Risk customers: {(rfm['churn_risk'] == 'Low Risk').sum()}")
    print(f"\nTop 5 customers by predicted CLV:")
    print(rfm[["frequency","recency","predicted_purchases_30d","predicted_clv_12m","churn_risk"]]
          .sort_values("predicted_clv_12m", ascending=False).head())

    # Save results
    os.makedirs("data/processed", exist_ok=True)
    rfm.to_csv("data/processed/ltv_results.csv")
    print("\nSaved to data/processed/ltv_results.csv")

    return rfm, bgf, ggf

if __name__ == "__main__":
    run_ltv_model()