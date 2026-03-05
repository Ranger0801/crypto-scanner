"""
routes.py
Flask Blueprint — all REST API endpoints.
"""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from sqlalchemy import desc, func
from database.db import db
from database.models import Coin, Signal
from config import Config

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ─────────────────────────────────────────────
# /api/signals  — latest signals
# ─────────────────────────────────────────────
@api_bp.route("/signals")
def get_signals():
    """
    Returns recent signals, optionally filtered.
    Query params: timeframe, direction, min_score, limit
    """
    timeframe  = request.args.get("timeframe")
    direction  = request.args.get("direction")
    min_score  = request.args.get("min_score", 0, type=int)
    limit      = request.args.get("limit", 50, type=int)
    since_hours = request.args.get("hours", 24, type=int)

    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    q = Signal.query.filter(Signal.timestamp >= cutoff, Signal.score >= min_score)

    if timeframe:
        q = q.filter(Signal.timeframe == timeframe)
    if direction:
        q = q.filter(Signal.direction == direction)

    signals = q.order_by(desc(Signal.timestamp)).limit(limit).all()
    return jsonify([s.to_dict() for s in signals])


# ─────────────────────────────────────────────
# /api/strong_signals  — score >= threshold
# ─────────────────────────────────────────────
@api_bp.route("/strong_signals")
def get_strong_signals():
    threshold = Config.STRONG_SIGNAL_SCORE
    cutoff    = datetime.utcnow() - timedelta(hours=24)

    signals = (
        Signal.query
        .filter(Signal.score >= threshold, Signal.timestamp >= cutoff)
        .order_by(desc(Signal.score), desc(Signal.timestamp))
        .limit(20)
        .all()
    )
    return jsonify([s.to_dict() for s in signals])


# ─────────────────────────────────────────────
# /api/top_gainers
# ─────────────────────────────────────────────
@api_bp.route("/top_gainers")
def get_top_gainers():
    limit = request.args.get("limit", 10, type=int)
    coins = (
        Coin.query
        .filter(Coin.change_24h.isnot(None))
        .order_by(desc(Coin.change_24h))
        .limit(limit)
        .all()
    )
    return jsonify([c.to_dict() for c in coins])


# ─────────────────────────────────────────────
# /api/top_losers
# ─────────────────────────────────────────────
@api_bp.route("/top_losers")
def get_top_losers():
    limit = request.args.get("limit", 10, type=int)
    coins = (
        Coin.query
        .filter(Coin.change_24h.isnot(None))
        .order_by(Coin.change_24h)
        .limit(limit)
        .all()
    )
    return jsonify([c.to_dict() for c in coins])


# ─────────────────────────────────────────────
# /api/coin/<symbol>
# ─────────────────────────────────────────────
@api_bp.route("/coin/<symbol>")
def get_coin(symbol: str):
    symbol = symbol.upper()
    coin   = Coin.query.filter_by(symbol=symbol).first_or_404()
    cutoff = datetime.utcnow() - timedelta(hours=48)

    recent_signals = (
        Signal.query
        .filter(Signal.coin_symbol == symbol, Signal.timestamp >= cutoff)
        .order_by(desc(Signal.timestamp))
        .limit(20)
        .all()
    )
    return jsonify({
        "coin":    coin.to_dict(),
        "signals": [s.to_dict() for s in recent_signals],
    })


# ─────────────────────────────────────────────
# /api/market_overview
# ─────────────────────────────────────────────
@api_bp.route("/market_overview")
def market_overview():
    coins   = Coin.query.all()
    cutoff  = datetime.utcnow() - timedelta(hours=24)
    total_signals = Signal.query.filter(Signal.timestamp >= cutoff).count()
    bullish = Signal.query.filter(Signal.direction == "bullish", Signal.timestamp >= cutoff).count()
    bearish = Signal.query.filter(Signal.direction == "bearish", Signal.timestamp >= cutoff).count()

    return jsonify({
        "coins":         [c.to_dict() for c in coins],
        "signal_counts": {
            "total":   total_signals,
            "bullish": bullish,
            "bearish": bearish,
        }
    })


# ─────────────────────────────────────────────
# /api/health
# ─────────────────────────────────────────────
@api_bp.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})
