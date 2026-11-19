
import streamlit as st

st.set_page_config(
    page_title="RetailSphere",
    page_icon="🛍️",
    layout="wide"
)

overview = st.Page(
    "pages/overview.py",
    title="Business Overview",
    icon=":material/dashboard:",
    default=True
)

products = st.Page(
    "pages/products.py",
    title="Product Performance",
    icon=":material/inventory_2:"
)

regional = st.Page(
    "pages/regional.py",
    title="Regional Analytics",
    icon=":material/public:"
)

assistant = st.Page(
    "pages/ai_assistant.py",
    title="AI Retail Assistant",
    icon=":material/smart_toy:"
)

navigation = st.navigation({
    "RetailSphere": [
        overview,
        products,
        regional,
        assistant
    ]
})

with st.sidebar:
    st.divider()
    st.caption("AI-Powered Retail Analytics")
    st.caption("Data: Databricks Gold snapshot")
    st.caption("LLM: Qwen 2.5 7B")
    st.caption("Observability: MLflow")

navigation.run()
