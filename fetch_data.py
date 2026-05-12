from pathlib import Path
import yfinance as yf
from config import TICKERS, LOOKBACK_YEARS

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

def main():
    symbols = list(TICKERS.values())
    raw = yf.download(symbols, period=LOOKBACK_YEARS, interval="1d", auto_adjust=True, progress=False)
    if raw.empty:
        raise RuntimeError("No data returned from Yahoo Finance. Check network/data availability.")
    close = raw["Close"] if "Close" in raw else raw
    close = close.rename(columns={v: k for k, v in TICKERS.items()})
    close.index.name = "Date"
    close.to_csv(DATA_DIR / "latest_prices.csv")
    print(f"Saved {DATA_DIR / 'latest_prices.csv'}")

if __name__ == "__main__":
    main()
