
import streamlit as st
import pandas as pd
import retail_agent

st.title("📍 Regional Analytics")
st.caption("Understand sales performance across Indian states.")

states = pd.DataFrame(retail_agent.state_sales)

states["total_revenue"] = pd.to_numeric(
    states["total_revenue"]
)

states = states.sort_values(
    "total_revenue", ascending=False
)

best = states.iloc[0]

st.metric(
    "Highest Revenue State",
    best["state"],
    f"₹{best['total_revenue']:,.0f}"
)

left, right = st.columns(2)

with left:
    st.subheader("State Revenue")
    st.bar_chart(
        states.set_index("state")["total_revenue"],
        horizontal=True
    )

with right:
    st.subheader("State Details")
    st.dataframe(states, use_container_width=True)
