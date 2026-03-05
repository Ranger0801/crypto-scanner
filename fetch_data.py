"""
fetch_data.py
Fetches OHLCV candle data from Binance (primary) and
spot price/market data from CoinGecko (supplementary).
"""

import logging
import requests
import pandas as pd
from config import Config

log = logging.getLogger(__name__)

BINANCE_BASE  = "https://api.binance.com"
COINGECKO_BASE = "https://api.coingecko.com/api/v3"


# ─────────────────────────────────────────────
# Binance — OHLCV candles
# ─────────────────────────────────────────────

def fetch_ohlcv(symbol: str, interval: str = "1h", limit: int = 100) -> pd.DataFrame | None:
    """
    Fetch candlestick data from Binance.

    Args:
        symbol:   e.g. "BTC"  (USDT pair is appended automatically)
        interval: Binance interval string — "1h", "4h", "1d", etc.
        limit:    Number of candles to fetch (max 1000)

    Returns:
        DataFrame with columns: open, high, low, close, volume
        or None on failure.
    """
    pair = f"{symbol}USDT"
    url  = f"{BINANCE_BASE}/api/v3/klines"
    params = {"symbol": pair, "interval": interval, "limit": limit}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json()

        df = pd.DataFrame(raw, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_vol", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])

        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col])

        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)

        return df[["open", "high", "low", "close", "volume"]]

    except requests.RequestException as e:
        log.error(f"[Binance] Failed to fetch {pair} {interval}: {e}")
        return None


# ─────────────────────────────────────────────
# CoinGecko — spot prices & market data
# ─────────────────────────────────────────────

def fetch_market_data(coin_ids: list[str]) -> dict:
    """
    Fetch current price, volume, and 24h change for a list of CoinGecko IDs.

    Returns:
        dict keyed by coingecko_id with price/volume/change fields.
    """
    ids_str = ",".join(coin_ids)
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ids_str,
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h",
    }
    if Config.COINGECKO_API_KEY:
        params["x_cg_demo_api_key"] = Config.COINGECKO_API_KEY

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        results = {}
        for coin in resp.json():
            results[coin["id"]] = {
                "symbol":     coin["symbol"].upper(),
                "name":       coin["name"],
                "price":      coin.get("current_price"),
                "volume_24h": coin.get("total_volume"),
                "change_24h": coin.get("price_change_percentage_24h"),
                "market_cap": coin.get("market_cap"),
            }
        return results

    except requests.RequestException as e:
        log.error(f"[CoinGecko] market data fetch failed: {e}")
        return {}
