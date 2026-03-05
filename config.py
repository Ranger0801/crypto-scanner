import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Works for both PostgreSQL (Supabase) and MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "")
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
```

Also update `requirements.txt` — replace `pymysql==1.1.1` with:
```
psycopg2-binary==2.9.9
