"""
app.py
Flask application factory — entry point for the Crypto Signal Scanner.
"""

import logging
from flask import Flask, render_template
from flask_cors import CORS

from config import Config
from database.db import db, init_db
from api.routes import api_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)
    db.init_app(app)

    # Register API Blueprint
    app.register_blueprint(api_bp)

    # Frontend page routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/scanner")
    def scanner():
        return render_template("scanner.html")

    @app.route("/coin/<symbol>")
    def coin_page(symbol):
        return render_template("coin.html", symbol=symbol.upper())

    return app


def main():
    app = create_app()

    # Create tables and seed coins
    init_db(app)

    # Start background scanner
    from scanner.scheduler import start_scheduler
    start_scheduler(app)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=Config.DEBUG,
        use_reloader=False,   # Must be False when using APScheduler
    )


if __name__ == "__main__":
    main()
