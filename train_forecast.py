from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error
from config import FORECAST_HORIZON_DAYS

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)


def make_features(series: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({"price": series}).dropna()
    for lag in [1, 2, 3, 5, 10, 20]:
        df[f"lag_{lag}"] = df["price"].shift(lag)
    df["ret_1"] = df["price"].pct_change(1)
    df["ret_5"] = df["price"].pct_change(5)
    df["ma_5"] = df["price"].rolling(5).mean()
    df["ma_20"] = df["price"].rolling(20).mean()
    df["vol_20"] = df["ret_1"].rolling(20).std()
    df["target"] = df["price"].shift(-1)
    return df.dropna()


def forecast_one(series: pd.Series, horizon: int):
    feat = make_features(series)
    X = feat.drop(columns=["target"])
    y = feat["target"]
    split = int(len(feat) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = RandomForestRegressor(n_estimators=300, random_state=42, min_samples_leaf=3)
    model.fit(X_train, y_train)
    pred_test = model.predict(X_test)
    mape = float(mean_absolute_percentage_error(y_test, pred_test) * 100)

    history = series.dropna().copy()
    future = []
    for _ in range(horizon):
        tmp = make_features(history)
        x_last = tmp.drop(columns=["target"]).iloc[[-1]]
        next_price = float(model.predict(x_last)[0])
        next_date = pd.bdate_range(history.index[-1] + pd.Timedelta(days=1), periods=1)[0]
        history.loc[next_date] = next_price
        future.append({"Date": next_date.strftime("%Y-%m-%d"), "Forecast": next_price})

    return pd.DataFrame(future), mape


def main():
    prices = pd.read_csv(DATA_DIR / "latest_prices.csv", index_col="Date", parse_dates=True)
    forecasts = []
    metrics = {}
    summary = []

    for commodity in prices.columns:
        fcst, mape = forecast_one(prices[commodity], FORECAST_HORIZON_DAYS)
        fcst["Commodity"] = commodity
        forecasts.append(fcst)
        metrics[commodity] = {"MAPE_pct": round(mape, 2)}

        latest = float(prices[commodity].dropna().iloc[-1])
        f30 = float(fcst["Forecast"].iloc[-1])
        chg = (f30 - latest) / latest * 100
        signal = "BUY/WATCH" if chg > 2 else "SELL/WATCH" if chg < -2 else "HOLD"
        summary.append({
            "Commodity": commodity,
            "Latest": latest,
            "Forecast_30D": f30,
            "Forecast_Change_pct": chg,
            "Signal": signal,
            "Model_MAPE_pct": mape,
        })

    pd.concat(forecasts, ignore_index=True).to_csv(DATA_DIR / "forecast_30d.csv", index=False)
    pd.DataFrame(summary).to_csv(DATA_DIR / "forecast_summary.csv", index=False)
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print("Saved forecast outputs in data/")

if __name__ == "__main__":
    main()
