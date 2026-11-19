
import streamlit as st
import pandas as pd
import retail_agent

st.title("📊 Business Overview")
st.caption("RetailSphere | Business Intelligence")

sales = pd.DataFrame(retail_agent.gold_sales)
products = pd.DataFrame(retail_agent.product_performance)
monthly = pd.DataFrame(retail_agent.monthly_revenue)

revenue = sales["item_revenue"].sum()
orders = monthly["total_orders"].sum()
units = products["units_sold"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", f"₹{revenue:,.0f}")
c2.metric("Delivered Orders", int(orders))
c3.metric("Units Sold", int(units))
c4.metric("Products", len(products))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Monthly Revenue")
    st.line_chart(
        monthly.set_index("sales_month")["total_revenue"]
    )

with right:
    st.subheader("Top Products")
    st.bar_chart(
        products.set_index("product_name")["total_revenue"],
        horizontal=True
    )

st.subheader("Gold Sales Data")
st.dataframe(sales, use_container_width=True)

st.download_button(
    "Download Sales CSV",
    sales.to_csv(index=False),
    "retailsphere_sales.csv",
    "text/csv"
)
