# file: app.py
import streamlit as st
import numpy as np
import pandas as pd
from applications_model import make_applications_model

st.set_page_config(page_title="Applications Backlog – What-if", layout="wide")
st.title("📮 Applications Backlog – What-if Simulator")

with st.sidebar:
    st.header("Controls")
    days = st.slider("Days to simulate", 7, 365, 180, step=1)
    seed = st.number_input("Random seed", min_value=0, max_value=10_000, value=42, step=1)
    initial_backlog = st.number_input("Initial backlog", 0, 10_000, 25, step=1)

    st.subheader("Arrivals (per day)")
    inflow_low = st.slider("Low", 0, 500, 30, 1)
    inflow_high = st.slider("High", inflow_low, 500, 60, 1)

    st.subheader("Processing capacity")
    capacity = st.slider("Daily processing capacity", 0, 500, 45, 1)
    variability_pct = st.slider("Capacity variability (±%)", 0, 100, 15, 1)
    variability = variability_pct / 100.0

    st.subheader("Policy")
    rejection_pct = st.slider("Rejection rate (%)", 0, 100, 50, 1)
    rejection_rate = rejection_pct / 100.0
    priority_spillover = st.checkbox("Allow processing some of today's accepted immediately", value=False)

# Build model (seed is handled by numpy RNG inside; we re-seed by recreating the model)
np.random.seed(seed)
model = make_applications_model(
    initial_backlog=initial_backlog,
    inflow_low=inflow_low, inflow_high=inflow_high,
    base_capacity=capacity, variability=variability,
    priority_spillover=priority_spillover,
    rejection_rate=rejection_rate,
    horizon=days
)

series = model.run(days)
backlog = series['backlog'][:days]

arrivals = model.params['todays_arrivals'][:days]
accepted = model.params['todays_accepted'][:days]
rejected = model.params['todays_rejected'][:days]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg arrivals/day", f"{arrivals.mean():.1f}")
col2.metric("Avg accepted/day", f"{accepted.mean():.1f}")
col3.metric("Avg rejected/day", f"{rejected.mean():.1f}")
col4.metric("Max backlog", int(backlog.max()))

# Charts
st.subheader("Backlog over time")
st.line_chart(pd.DataFrame({"Backlog": backlog}))

st.subheader("Daily arrivals split")
st.line_chart(pd.DataFrame({
    "Arrivals (total)": arrivals,
    "Accepted": accepted,
    "Rejected": rejected
}))

# Tabular + download
df = pd.DataFrame({
    "day": np.arange(days),
    "arrivals_total": arrivals,
    "accepted": accepted,
    "rejected": rejected,
    "backlog": backlog
})
st.download_button(
    "Download CSV",
    df.to_csv(index=False).encode("utf-8"),
    file_name="applications_simulation.csv",
    mime="text/csv"
)

st.caption(
    "Tip: raise capacity or lower variability to control backlog; change rejection rate to see instant impact on accepted inflow."
)
