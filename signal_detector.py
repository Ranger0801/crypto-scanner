"""
signal_detector.py
Detects trading signals from indicator values and assigns a composite score.
"""

import json
import logging
from datetime import datetime
from database.db import db
from database.models import Signal

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Signal scoring weights
# ─────────────────────────────────────────────
SCORE_MAP = {
    "MACD Bullish":    2,
    "MACD Bearish":    2,
    "EMA Bullish":     2,
    "EMA Bearish":     2,
    "Volume Spike":    1,
    "RSI Oversold":    1,
    "RSI Overbought":  1,
}

STRONG_SIGNAL_SCORE = 4


def detect_signals(symbol: str, timeframe: str, ind: dict) -> list[dict]:
    """
    Evaluate indicators and return a list of detected signal dicts.
    Each dict contains: signal_type, direction, score, details.
    """
    signals = []

    # ── MACD Crossover ─────────────────────────
    macd_cross_up   = ind["macd_prev"] < ind["macd_sig_prev"] and ind["macd_line"] > ind["macd_signal"]
    macd_cross_down = ind["macd_prev"] > ind["macd_sig_prev"] and ind["macd_line"] < ind["macd_signal"]

    if macd_cross_up:
        signals.append(_make_signal("MACD Bullish", "bullish", ind))
    elif macd_cross_down:
        signals.append(_make_signal("MACD Bearish", "bearish", ind))

    # ── EMA Crossover ──────────────────────────
    if ind["ema20"] > ind["ema50"]:
        signals.append(_make_signal("EMA Bullish", "bullish", ind))
    elif ind["ema20"] < ind["ema50"]:
        signals.append(_make_signal("EMA Bearish", "bearish", ind))

    # ── Volume Spike ───────────────────────────
    if ind["volume_ratio"] >= 2.0:
        signals.append(_make_signal("Volume Spike", "neutral", ind))

    # ── RSI Extremes ───────────────────────────
    if ind["rsi"] < 30:
        signals.append(_make_signal("RSI Oversold", "bullish", ind))
    elif ind["rsi"] > 70:
        signals.append(_make_signal("RSI Overbought", "bearish", ind))

    return signals


def compute_composite_score(signals: list[dict]) -> int:
    """Sum individual signal scores into a composite trade strength score."""
    return sum(SCORE_MAP.get(s["signal_type"], 1) for s in signals)


def save_signals(app, symbol: str, timeframe: str, signals: list[dict], score: int):
    """Persist detected signals to PostgreSQL."""
    if not signals:
        return

    with app.app_context():
        for sig in signals:
            record = Signal(
                coin_symbol = symbol,
                signal_type = sig["signal_type"],
                direction   = sig["direction"],
                timeframe   = timeframe,
                score       = score,
                details     = json.dumps(sig["details"]),
                timestamp   = datetime.utcnow(),
            )
            db.session.add(record)
        db.session.commit()
        log.info(f"[{symbol} {timeframe}] Saved {len(signals)} signal(s). Score: {score}")


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _make_signal(signal_type: str, direction: str, ind: dict) -> dict:
    return {
        "signal_type": signal_type,
        "direction":   direction,
        "details": {
            "macd":         ind["macd_line"],
            "macd_signal":  ind["macd_signal"],
            "ema20":        ind["ema20"],
            "ema50":        ind["ema50"],
            "rsi":          ind["rsi"],
            "volume_ratio": ind["volume_ratio"],
            "close":        ind["close"],
        }
    }
