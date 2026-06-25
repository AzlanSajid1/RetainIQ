import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.clean_data import load_orders

st.set_page_config(page_title="RetainIQ", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    orders = load_orders()
    rfm = pd.read_csv("data/processed/rfm_results.csv")
    ltv = pd.read_csv("data/processed/ltv_results.csv")
    merged = rfm.merge(
        ltv[["customer_id", "churn_risk", "predicted_clv_12m", "predicted_purchases_30d"]],
        on="customer_id"
    )
    return orders, merged

orders, customers = load_data()

# Sidebar navigation
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
st.sidebar.title("RetainIQ")
st.sidebar.caption("Churn Prediction Dashboard")
page = st.sidebar.radio("", ["Overview", "At-Risk Customers", "Cohort Analysis"])

# ── PAGE 1: OVERVIEW ──────────────────────────────────────────────
if page == "Overview":
    st.title("Store Overview")
    st.caption("Powered by BG/NBD + Gamma-Gamma models")

    total = len(customers)
    high_risk = (customers["churn_risk"] == "High Risk").sum()
    pct_risk = round(high_risk / total * 100, 1)
    revenue_at_risk = customers[customers["churn_risk"] == "High Risk"]["predicted_clv_12m"].sum()
    total_clv = customers["predicted_clv_12m"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", total)
    col2.metric("At Risk", high_risk, f"{pct_risk}% of base")
    col3.metric("Revenue at Risk (12m)", f"PKR {revenue_at_risk:,.0f}")
    col4.metric("Total Predicted CLV", f"PKR {total_clv:,.0f}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Segments")
        seg_counts = customers["segment"].value_counts().reset_index()
        seg_counts.columns = ["segment", "count"]
        colors = {"Champions": "#2ecc71", "Loyal": "#3498db", "At Risk": "#f39c12", "Lost": "#e74c3c"}
        fig = px.pie(seg_counts, values="count", names="segment",
                     color="segment", color_discrete_map=colors, hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Avg CLV by Segment")
        clv_seg = customers.groupby("segment")["predicted_clv_12m"].mean().reset_index()
        clv_seg.columns = ["segment", "avg_clv"]
        clv_seg = clv_seg.sort_values("avg_clv", ascending=True)
        fig2 = px.bar(clv_seg, x="avg_clv", y="segment", orientation="h",
                      color="segment", color_discrete_map=colors)
        fig2.update_layout(showlegend=False, xaxis_title="Avg Predicted CLV (PKR)", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Monthly Order Volume")
    orders["month"] = orders["created_at"].dt.to_period("M").astype(str)
    monthly = orders.groupby("month").agg(orders=("order_id","count"), revenue=("total_price","sum")).reset_index()
    fig3 = px.line(monthly, x="month", y="revenue", markers=True)
    fig3.update_layout(xaxis_title="Month", yaxis_title="Revenue (PKR)")
    st.plotly_chart(fig3, use_container_width=True)

# ── PAGE 2: AT-RISK CUSTOMERS ─────────────────────────────────────
elif page == "At-Risk Customers":
    st.title("At-Risk Customers")
    st.caption("Customers predicted to churn — export and target with winback campaigns")

    risk_filter = st.selectbox("Filter by risk level", ["All", "High Risk", "Medium Risk", "Low Risk"])

    df = customers.copy()
    if risk_filter != "All":
        df = df[df["churn_risk"] == risk_filter]

    df_display = df[[
        "customer_id", "segment", "recency", "frequency",
        "monetary", "predicted_purchases_30d", "predicted_clv_12m", "churn_risk"
    ]].sort_values("predicted_clv_12m", ascending=False).reset_index(drop=True)

    df_display.columns = [
        "Customer ID", "Segment", "Days Since Last Order", "Total Orders",
        "Total Spent (PKR)", "Predicted Purchases (30d)", "Predicted CLV (12m)", "Churn Risk"
    ]

    st.dataframe(df_display, use_container_width=True, height=400)

    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Export for Klaviyo / Email Campaign",
        data=csv,
        file_name="at_risk_customers.csv",
        mime="text/csv"
    )

    st.info(f"Showing {len(df_display)} customers. Upload the exported CSV to Klaviyo or Mailchimp to run a winback campaign.")

# ── PAGE 3: COHORT ANALYSIS ───────────────────────────────────────
elif page == "Cohort Analysis":
    st.title("Cohort Retention Analysis")
    st.caption("How well are customer cohorts retained over time?")

    orders["cohort"] = orders.groupby("customer_id")["created_at"].transform("min").dt.to_period("M").astype(str)
    orders["order_month"] = orders["created_at"].dt.to_period("M").astype(str)

    cohort_data = orders.groupby(["cohort", "order_month"])["customer_id"].nunique().reset_index()
    cohort_data.columns = ["cohort", "order_month", "customers"]

    cohort_size = cohort_data[cohort_data["cohort"] == cohort_data["order_month"]][["cohort", "customers"]]
    cohort_size.columns = ["cohort", "cohort_size"]
    cohort_data = cohort_data.merge(cohort_size, on="cohort")
    cohort_data["retention"] = (cohort_data["customers"] / cohort_data["cohort_size"] * 100).round(1)

    pivot = cohort_data.pivot(index="cohort", columns="order_month", values="retention")

    fig = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn",
        aspect="auto",
        title="Retention Rate % by Cohort"
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Cohort")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Segment Distribution Over Time")
    seg_time = customers.merge(
        orders[["customer_id","order_month"]].drop_duplicates(),
        on="customer_id"
    )
    seg_month = seg_time.groupby(["order_month","segment"])["customer_id"].nunique().reset_index()
    fig2 = px.bar(seg_month, x="order_month", y="customer_id", color="segment",
                  color_discrete_map={"Champions":"#2ecc71","Loyal":"#3498db","At Risk":"#f39c12","Lost":"#e74c3c"})
    fig2.update_layout(xaxis_title="Month", yaxis_title="Customers", barmode="stack")
    st.plotly_chart(fig2, use_container_width=True)