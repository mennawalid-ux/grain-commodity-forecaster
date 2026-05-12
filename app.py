from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Grain Futures Forecaster", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

st.title("Grain Futures Price Forecaster")
st.caption("Corn, Wheat, and Soybean futures analytics for trading desk decision support")

price_file = DATA_DIR / "latest_prices.csv"
forecast_file = DATA_DIR / "forecast_30d.csv"
summary_file = DATA_DIR / "forecast_summary.csv"

if not price_file.exists() or not forecast_file.exists():
    st.error("Data not found. Run: python scripts/fetch_data.py && python scripts/train_forecast.py")
    st.stop()

prices = pd.read_csv(price_file, index_col="Date", parse_dates=True)
forecast = pd.read_csv(forecast_file, parse_dates=["Date"])
summary = pd.read_csv(summary_file)

commodities = list(prices.columns)
commodity = st.sidebar.selectbox("Commodity", commodities)
horizon = st.sidebar.slider("Forecast days to display", 5, 30, 30)
threshold = st.sidebar.number_input("Alert threshold %", value=2.0, step=0.5)

latest = prices[commodity].dropna().iloc[-1]
previous = prices[commodity].dropna().iloc[-2]
daily_change = (latest - previous) / previous * 100
row = summary[summary["Commodity"] == commodity].iloc[0]
forecast_change = row["Forecast_Change_pct"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest price", f"{latest:,.2f}", f"{daily_change:.2f}%")
c2.metric("30D forecast", f"{row['Forecast_30D']:,.2f}", f"{forecast_change:.2f}%")
c3.metric("Signal", row["Signal"])
c4.metric("Model MAPE", f"{row['Model_MAPE_pct']:.2f}%")

if forecast_change >= threshold:
    st.warning(f"Alert: {commodity} forecast increase is above {threshold:.1f}%")
elif forecast_change <= -threshold:
    st.warning(f"Alert: {commodity} forecast decrease is below -{threshold:.1f}%")
else:
    st.success("No major alert under the selected threshold.")

hist = prices[[commodity]].reset_index().rename(columns={commodity: "Price"})
fc = forecast[forecast["Commodity"] == commodity].head(horizon).copy()

fig = px.line(hist, x="Date", y="Price", title=f"Historical Daily Price - {commodity}")
st.plotly_chart(fig, use_container_width=True)

fig2 = px.line(fc, x="Date", y="Forecast", title=f"Forecast Next {horizon} Business Days - {commodity}")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Trading Desk Summary")
st.dataframe(summary, use_container_width=True)

st.subheader("Decision Support Notes")
st.write("This tool is a forecasting and alerting dashboard, not an automated trading system. Combine signals with fundamentals such as USDA reports, weather risk, export demand, currency moves, and geopolitical news.")
