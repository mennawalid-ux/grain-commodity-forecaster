from pathlib import Path
import os
import requests
import pandas as pd
from config import ALERT_THRESHOLD_PCT

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def send_telegram(text: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram credentials not set; printing alert only.")
        print(text)
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=20).raise_for_status()


def main():
    summary_path = DATA_DIR / "forecast_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError("Run train_forecast.py before send_alerts.py")
    df = pd.read_csv(summary_path)
    rows = []
    for _, r in df.iterrows():
        chg = float(r["Forecast_Change_pct"])
        if abs(chg) >= ALERT_THRESHOLD_PCT:
            direction = "increase" if chg > 0 else "decrease"
            rows.append(f"{r['Commodity']}: expected {direction} {chg:.2f}% | Signal: {r['Signal']}")
    if rows:
        send_telegram("Grain Futures Alert\n" + "\n".join(rows))
    else:
        print("No alerts triggered.")

if __name__ == "__main__":
    main()
