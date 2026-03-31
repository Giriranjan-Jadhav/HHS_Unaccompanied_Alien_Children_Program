import streamlit as st
import pandas as pd

df = pd.read_excel(r"C:\Users\GIRIRANJAN\OneDrive\Desktop\HHS_Unaccompanied_Alien_Children_Program.xlsx")
df = pd.read_excel("HHS_Unaccompanied_Alien_Children_Program.xlsx")

# Ensure proper data types
df["Date"] = pd.to_datetime(df["Date"])
df["Backlog_Indicator"] = pd.to_numeric(df["Backlog_Indicator"], errors="coerce")

st.set_page_config(page_title="System Load Dashboard", layout="wide")
st.title("System Load Dashboard")

st.sidebar.header("Filters")

start_date = st.sidebar.date_input("Start Date", df["Date"].min())
end_date = st.sidebar.date_input("End Date", df["Date"].max())

metrics = st.sidebar.multiselect(
    "Select Metrics",
    ["Children _in_CBP_custody", "Children_in_HHS_Care", "Net_Daily_Intake", "Backlog_Indicator"],
    default=["Children _in_CBP_custody", "Children_in_HHS_Care"]
)

granularity = st.sidebar.selectbox(
    "Time Granularity",
    ["Daily", "Weekly", "Monthly"]
)

filtered_df = df[
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date))
]

if granularity == "Weekly":
    filtered_df = filtered_df.resample("W", on="Date").mean(numeric_only=True).reset_index()
elif granularity == "Monthly":
    filtered_df = filtered_df.resample("M", on="Date").mean(numeric_only=True).reset_index()

st.subheader("KPI Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg CBP Load", round(filtered_df["Children _in_CBP_custody"].mean(), 2))
col2.metric("Avg HHS Load", round(filtered_df["Children_in_HHS_Care"].mean(), 2))
col3.metric("Total Intake", int(filtered_df["Net_Daily_Intake"].sum()))
col4.metric("Avg Backlog", round(filtered_df["Backlog_Indicator"].mean(), 2))

st.subheader("System Load Overview")

if metrics:
    chart_df = filtered_df.set_index("Date")[metrics]
    st.line_chart(chart_df)
else:
    st.warning("Please select at least one metric")

st.subheader("⚠️ Pressure & Stress Identification")

rolling_df = filtered_df.copy()
rolling_df = rolling_df.sort_values("Date")


for col in ["Children _in_CBP_custody", "Children_in_HHS_Care"]:
    rolling_df[f"{col}_7day_avg"] = rolling_df[col].rolling(window=7).mean()
    rolling_df[f"{col}_14day_avg"] = rolling_df[col].rolling(window=14).mean()


for col in ["Children _in_CBP_custody", "Children_in_HHS_Care"]:
    rolling_df[f"{col}_volatility"] = rolling_df[col].rolling(window=7).std()


st.markdown("**Rolling Averages (7-day & 14-day)**")
rolling_chart = rolling_df.set_index("Date")[[
    "Children _in_CBP_custody_7day_avg",
    "Children _in_CBP_custody_14day_avg",
    "Children_in_HHS_Care_7day_avg",
    "Children_in_HHS_Care_14day_avg"
]]
st.line_chart(rolling_chart)

st.markdown("**Variability (7-day Standard Deviation)**")
volatility_chart = rolling_df.set_index("Date")[[
    "Children _in_CBP_custody_volatility",
    "Children_in_HHS_Care_volatility"
]]
st.line_chart(volatility_chart)

st.subheader("CBP vs HHS Load Comparison")

comparison_df = filtered_df.set_index("Date")[[
    "Children _in_CBP_custody",
    "Children_in_HHS_Care"
]]
st.line_chart(comparison_df)

st.subheader("Net Intake & Backlog Trends")

trend_df = filtered_df.set_index("Date")[[
    "Net_Daily_Intake",
    "Backlog_Indicator"
]]
st.line_chart(trend_df)
