"""
setup_db.py
Run this ONCE before starting the app for the first time.
Creates the MySQL database + all tables + seeds the coin list.

Usage:
    python setup_db.py
"""

import sys
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "crypto_signals")


def create_database():
    print(f"🔌 Connecting to MySQL at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")
    try:
        conn = pymysql.connect(
            host=DB_HOST, port=DB_PORT,
            user=DB_USER, password=DB_PASS,
            charset="utf8mb4"
        )
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        conn.commit()
        conn.close()
        print(f"✅ Database '{DB_NAME}' ready.")
    except pymysql.Error as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\nCheck your .env file:")
        print(f"  DB_USER={DB_USER}")
        print(f"  DB_HOST={DB_HOST}:{DB_PORT}")
        print(f"  DB_NAME={DB_NAME}")
        sys.exit(1)


def create_tables_and_seed():
    print("📦 Creating tables and seeding coin list...")
    from app import create_app
    from database.db import init_db

    app = create_app()
    init_db(app)   # creates tables + seeds coins from coin_list.json
    print("✅ Tables created and coins seeded.")


def verify():
    """Quick sanity check — print the coin count."""
    from app import create_app
    from database.models import Coin

    app = create_app()
    with app.app_context():
        count = Coin.query.count()
        print(f"✅ Verification: {count} coin(s) in database.")


if __name__ == "__main__":
    create_database()
    create_tables_and_seed()
    verify()
    print("\n🚀 Setup complete! Now run:  python app.py")
