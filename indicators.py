"""
indicators.py
Calculates all technical indicators using pandas-ta.
Returns a clean dict of indicator values for signal detection.
"""

import logging
import pandas as pd
import pandas_ta as ta

log = logging.getLogger(__name__)


def calculate_indicators(df: pd.DataFrame) -> dict | None:
    """
    Given an OHLCV DataFrame, calculate all technical indicators.

    Returns a dict with the latest values for each indicator,
    or None if calculation fails.
    """
    if df is None or len(df) < 50:
        log.warning("Not enough candle data to calculate indicators (need ≥50 rows).")
        return None

    try:
        close  = df["close"]
        volume = df["volume"]

        # ── MACD ────────────────────────────────
        macd_df = ta.macd(close, fast=12, slow=26, signal=9)
        macd_line   = macd_df.iloc[-1]["MACD_12_26_9"]
        macd_signal = macd_df.iloc[-1]["MACDs_12_26_9"]
        macd_prev   = macd_df.iloc[-2]["MACD_12_26_9"]
        macd_sig_prev = macd_df.iloc[-2]["MACDs_12_26_9"]

        # ── EMA ─────────────────────────────────
        ema20 = ta.ema(close, length=20).iloc[-1]
        ema50 = ta.ema(close, length=50).iloc[-1]

        # ── RSI ─────────────────────────────────
        rsi = ta.rsi(close, length=14).iloc[-1]

        # ── Volume Spike ────────────────────────
        avg_volume   = volume.rolling(20).mean().iloc[-1]
        latest_volume = volume.iloc[-1]
        volume_ratio  = latest_volume / avg_volume if avg_volume > 0 else 0

        return {
            "macd_line":      round(float(macd_line),   6),
            "macd_signal":    round(float(macd_signal), 6),
            "macd_prev":      round(float(macd_prev),   6),
            "macd_sig_prev":  round(float(macd_sig_prev), 6),
            "ema20":          round(float(ema20), 4),
            "ema50":          round(float(ema50), 4),
            "rsi":            round(float(rsi),   2),
            "volume":         round(float(latest_volume), 2),
            "avg_volume":     round(float(avg_volume),    2),
            "volume_ratio":   round(float(volume_ratio),  2),
            "close":          round(float(close.iloc[-1]), 6),
        }

    except Exception as e:
        log.error(f"Indicator calculation error: {e}")
        return None
