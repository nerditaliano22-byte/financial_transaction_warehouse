import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(page_title="Time Analysis 2024", layout="wide")

# Config: Point to the data directory
DATA_DIR = "data"

@st.cache_data(show_spinner=False)
def load_data():
    files = {
        "FACT": os.path.join(DATA_DIR, "fact_transactions.csv"),
        "TIME": os.path.join(DATA_DIR, "dim_time.csv"),
        "SYM":  os.path.join(DATA_DIR, "dim_symbol.csv"),
    }
    
    missing = [f for f in files.values() if not os.path.exists(f)]
    if missing:
        st.error(f"Missing files: {', '.join(missing)}. Run 'python src/etl.py' first.")
        st.stop()

    return (
        pd.read_csv(files["FACT"]),
        pd.read_csv(files["TIME"], parse_dates=["Date"]),
        pd.read_csv(files["SYM"]),
    )

fact, dim_time, dim_sym = load_data()

# Merge for visualization
fact = (
    fact
    .merge(dim_time[["TimeKey", "Date", "Quarter"]], on="TimeKey", how="left")
    .merge(dim_sym[["SymbolKey", "Symbol", "sector", "industry"]], on="SymbolKey", how="left")
)

st.title("Time Analysis – BUY + SELL (2024)")

# Sidebar Date Filter
st.sidebar.header("Date range")
start_def, end_def = date(2024, 1, 1), date(2024, 12, 31)
date_range = st.sidebar.date_input("Select start & end", (start_def, end_def), min_value=start_def, max_value=end_def)

if len(date_range) == 2:
    start_date, end_date = date_range
    if start_date > end_date:
        st.sidebar.error("Start date must be ≤ end date.")
        st.stop()
else:
    start_date = end_date = date_range[0] if date_range else start_def

# Filter Data
df = fact[
    (fact["Date"].dt.date.between(start_date, end_date)) &
    (fact["TransactionType"].isin(["BUY", "SELL"]))
].copy()

if df.empty:
    st.warning("No BUY/SELL data for the selected period.")
    st.stop()

#  Visualizations 
st.subheader("Daily transactions")
daily = df.groupby(df["Date"].dt.date)["TransactionCount"].sum().reset_index()
fig_line = px.line(daily, x="Date", y="TransactionCount", title="Daily Trend", template="plotly_white")
st.plotly_chart(fig_line, use_container_width=True)

st.subheader("Top entities")
col1, col2 = st.columns(2)

def create_stacked_bar(data, x_col, title, tickangle=0):
    total_order = data.groupby(x_col)["TransactionCount"].sum().sort_values(ascending=False).index
    data[x_col] = pd.Categorical(data[x_col], categories=total_order, ordered=True)
    data = data.sort_values(x_col)
    fig = px.bar(
        data, x=x_col, y="TransactionCount", color="TransactionType",
        title=title, template="plotly_white", text_auto=True,
        color_discrete_map={'BUY': '#2E8B57', 'SELL': '#4169E1'}
    )
    if tickangle: fig.update_xaxes(tickangle=tickangle)
    return fig

with col1:
    top_sym = df.groupby(["Symbol"])["TransactionCount"].sum().nlargest(3).index
    sym_data = df[df["Symbol"].isin(top_sym)].groupby(["Symbol", "TransactionType"])["TransactionCount"].sum().reset_index()
    st.plotly_chart(create_stacked_bar(sym_data, "Symbol", "Top 3 Symbols"), use_container_width=True)

with col2:
    top_sec = df.groupby(["sector"])["TransactionCount"].sum().nlargest(5).index
    sec_data = df[df["sector"].isin(top_sec)].groupby(["sector", "TransactionType"])["TransactionCount"].sum().reset_index()
    st.plotly_chart(create_stacked_bar(sec_data, "sector", "Top 5 Sectors", 45), use_container_width=True)