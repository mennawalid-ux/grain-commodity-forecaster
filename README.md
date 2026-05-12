# Grain Futures Price Forecaster

Interactive and automated Streamlit website for grain futures analytics and daily decision support.

## Commodities

- Corn Futures: `ZC=F`
- Wheat Futures: `ZW=F`
- Soybean Futures: `ZS=F`

## Features

- Extracts daily futures prices from Yahoo Finance using `yfinance`
- Builds 30-business-day forecasts with a machine learning model
- Shows interactive historical and forecast charts
- Generates trading desk signals: `BUY/WATCH`, `SELL/WATCH`, or `HOLD`
- Sends Telegram alerts when forecast movement exceeds the alert threshold
- Automates daily updates with GitHub Actions
- Ready for Streamlit Cloud deployment

## Local setup

```bash
pip install -r requirements.txt
python scripts/fetch_data.py
python scripts/train_forecast.py
streamlit run app.py
```

## GitHub deployment

1. Create a new GitHub repository.
2. Upload all files in this folder.
3. Go to Streamlit Community Cloud.
4. Connect your GitHub repository.
5. Set the app entry file as `app.py`.
6. Deploy.

## Daily automation

The file `.github/workflows/daily_update.yml` runs every weekday at 07:00 UTC.

To enable Telegram alerts, add these GitHub repository secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Important trading note

This app supports decision makers but does not replace trader judgment. Grain futures can move sharply due to USDA reports, weather, export demand, energy prices, FX, interest rates, geopolitical events, and liquidity shocks.
