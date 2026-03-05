"""
scheduler.py
Orchestrates the full scan cycle using APScheduler.
Every N minutes: fetch → indicators → detect → save → update coins.
"""

import json
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from scanner.fetch_data import fetch_ohlcv, fetch_market_data
from scanner.indicators import calculate_indicators
from scanner.signal_detector import detect_signals, compute_composite_score, save_signals

log = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="UTC")


def run_scan(app):
    """Full scan cycle: called on schedule and on startup."""
    log.info("🔍 Starting scan cycle...")

    coin_file = os.path.join(os.path.dirname(__file__), "..", "data", "coin_list.json")
    with open(coin_file) as f:
        coins = json.load(f)["coins"]

    # ── Update market data (prices, volume, change) ─────
    coingecko_ids = [c["coingecko_id"] for c in coins]
    market_data   = fetch_market_data(coingecko_ids)
    _update_coin_prices(app, coins, market_data)

    # ── Scan each coin × each timeframe ─────────────────
    for coin in coins:
        symbol = coin["symbol"]
        for tf in Config.TIMEFRAMES:
            log.info(f"  Scanning {symbol} [{tf}]...")
            df  = fetch_ohlcv(symbol, interval=tf, limit=100)
            ind = calculate_indicators(df)
            if ind is None:
                continue

            signals = detect_signals(symbol, tf, ind)
            if not signals:
                continue

            score = compute_composite_score(signals)
            save_signals(app, symbol, tf, signals, score)

    log.info("✅ Scan cycle complete.")


def _update_coin_prices(app, coins: list, market_data: dict):
    """Update Coin table with latest CoinGecko prices."""
    from database.db import db
    from database.models import Coin

    with app.app_context():
        for coin in coins:
            cg_id = coin["coingecko_id"]
            data  = market_data.get(cg_id)
            if not data:
                continue

            record = Coin.query.filter_by(symbol=coin["symbol"]).first()
            if record:
                record.price      = data.get("price")
                record.volume_24h = data.get("volume_24h")
                record.change_24h = data.get("change_24h")
                record.market_cap = data.get("market_cap")

        db.session.commit()


def start_scheduler(app):
    """Start background scheduler and run an immediate first scan."""
    interval = Config.SCAN_INTERVAL_MINUTES

    _scheduler.add_job(
        func=run_scan,
        args=[app],
        trigger="interval",
        minutes=interval,
        id="crypto_scan",
        replace_existing=True,
    )
    _scheduler.start()
    log.info(f"⏰ Scheduler started — scanning every {interval} minutes.")

    # Run immediately on startup (in a thread to not block Flask)
    import threading
    t = threading.Thread(target=run_scan, args=[app], daemon=True)
    t.start()


def stop_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
