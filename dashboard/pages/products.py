
import streamlit as st
import pandas as pd
import retail_agent

st.title("📦 Product Performance")
st.caption("Explore product-level sales and revenue.")

products = pd.DataFrame(retail_agent.product_performance)

products["total_revenue"] = pd.to_numeric(
    products["total_revenue"]
)

products = products.sort_values(
    "total_revenue", ascending=False
)

st.metric(
    "Total Product Revenue",
    f"₹{products['total_revenue'].sum():,.0f}"
)

st.subheader("Revenue by Product")
st.bar_chart(
    products.set_index("product_name")["total_revenue"],
    horizontal=True
)

st.subheader("Product Details")
st.dataframe(products, use_container_width=True)

selected = st.selectbox(
    "Explore a product",
    products["product_name"].tolist()
)

product = products[
    products["product_name"] == selected
].iloc[0]

a, b = st.columns(2)
a.metric("Units Sold", int(product["units_sold"]))
b.metric("Revenue", f"₹{product['total_revenue']:,.0f}")
