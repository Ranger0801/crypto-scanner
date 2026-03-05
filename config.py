import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # ── MySQL connection ──────────────────────────────────────────
    # Format: mysql+pymysql://user:password@host:port/dbname
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "crypto_signals")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,      # avoid MySQL's 8h timeout dropping connections
        "pool_pre_ping": True,    # test connection before using it
    }

    # Scanner settings
    SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", 5))
    STRONG_SIGNAL_THRESHOLD = int(os.getenv("STRONG_SIGNAL_THRESHOLD", 4))

    # API Keys (CoinGecko free tier needs no key)
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")
    BINANCE_API_KEY   = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET    = os.getenv("BINANCE_SECRET", "")

    # Coins to scan
    COINS = ["BTC", "ETH", "SOL", "LINK", "AVAX", "BNB", "ADA", "DOT", "MATIC", "DOGE"]

    # Timeframes (Binance kline intervals)
    TIMEFRAMES = ["1h", "4h", "1d"]

    # Telegram (optional)
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
