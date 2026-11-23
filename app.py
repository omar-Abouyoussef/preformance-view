
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portfolio Performance", layout="wide")
st.title("Portfolio Performance")

FILES = {
    "7arees": "Cumulative Returns 7arees.xlsx",
    "Alfa": "Cumulative Returns alfa V4.xlsx"
}

DATA_IS_CUMULATIVE = True  # False if Excel files contain daily returns instead

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()
    df = df[["Portfolio", "EGX30 Benchmark", "Fixed Income"]].apply(pd.to_numeric, errors="coerce").dropna()
    if df.abs().max().max() <= 2: df *= 100  # Convert decimals to percentages
    return df

strategy = st.selectbox("Portfolio", ["7arees", "Alfa"])
data = load_data(FILES[strategy])

# Default viewing period
start_date, end_date = data.index.min().date(), data.index.max().date()

start_date, end_date = st.slider(
    "Viewing Period",
    min_value=start_date,
    max_value=end_date,
    value=(start_date, end_date),
    format="YYYY-MM-DD"
)

data = data.loc[str(start_date):str(end_date)]

# Convert cumulative returns into wealth; alternatively compound daily returns
wealth = (1 + data / 100).cumprod() if not DATA_IS_CUMULATIVE else 1 + data / 100

# Rebase performance to 0% at the beginning of the selected period
performance = (wealth / wealth.iloc[0] - 1) * 100

# Drawdowns from running historical peaks
drawdowns = (wealth / wealth.cummax() - 1) * 100

for df, title, ylabel in [
    (performance, "Cumulative Performance", "Return (%)"),
    (drawdowns, "Drawdown", "Drawdown (%)")
]:
    fig = px.line(df, title=title, labels={"Date": "Date", "value": ylabel, "variable": ""})
    fig.update_layout(
        template="plotly_white", hovermode="x unified", height=500,
        yaxis_ticksuffix="%", legend_title_text="", title_x=0.02,
        margin=dict(l=50, r=25, t=60, b=40)
    )
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.6)
    st.plotly_chart(fig, use_container_width=True)
