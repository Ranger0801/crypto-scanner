import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:SqqG9cQKHPD2ebn7@db.rhnkyemmzgolmzpjvfgr.supabase.co:5432/postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", 5))
    STRONG_SIGNAL_THRESHOLD = int(os.getenv("STRONG_SIGNAL_THRESHOLD", 4))
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")
    COINS = ["BTC","ETH","SOL","LINK","AVAX","BNB","ADA","DOT","MATIC","DOGE"]
    TIMEFRAMES = ["1h", "4h", "1d"]
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")
