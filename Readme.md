# RetainIQ — Churn Prediction Dashboard for Shopify Stores

A machine learning tool that predicts customer churn and identifies at-risk customers for Shopify merchants. Built with BG/NBD + Gamma-Gamma models and deployed as an interactive dashboard.

**Live Demo:** https://retainiq-2ha4.onrender.com

---

## What It Does

- Predicts which customers are likely to churn in the next 30 days
- Estimates 12-month Customer Lifetime Value (CLV) per customer
- Segments customers into Champions, Loyal, At Risk, and Lost groups
- Exports at-risk customer lists as CSV for Klaviyo/Mailchimp winback campaigns
- Visualizes cohort retention heatmaps

## Why It Matters

The average ecommerce CAC is $68–84, up 60% in two years. Merchants spending heavily on acquisition have zero visibility into which customers are about to churn. RetainIQ gives them that visibility in one dashboard.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Source | Shopify Admin REST API |
| Data Processing | Python, Pandas |
| ML Models | BG/NBD (lifetimes), Gamma-Gamma, KMeans |
| Frontend | Streamlit, Plotly |
| Deployment | Render |

---

## ML Models Explained

**BG/NBD (Beta-Geometric/Negative Binomial Distribution)**
Models each customer's purchase timing as a Poisson process with a dropout probability after each transaction. Takes only 3 inputs per customer — frequency, recency, and age — and outputs probability of future purchases.

**Gamma-Gamma**
Predicts average order value for active customers. Combined with BG/NBD to produce 12-month CLV estimates.

**RFM + KMeans Clustering**
Segments customers by Recency, Frequency, and Monetary value into 4 behavioral clusters automatically labeled by spend level.

---

## Project Structure

retainiq/

├── app.py                  # Streamlit dashboard

├── src/

│   ├── clean_data.py       # Data loading and cleaning

│   ├── ltv_model.py        # BG/NBD + Gamma-Gamma models

│   ├── rfm_model.py        # RFM segmentation

│   └── fetch_data.py       # Shopify API integration

├── data/

│   └── processed/          # Model outputs

└── requirements.txt
---

## Local Setup

```bash
git clone https://github.com/AzlanSajid1/RetainIQ.git
cd RetainIQ
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Author

**Azlan Sajid** — BS Data Science, FAST-NUCES Lahore