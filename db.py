from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance — imported everywhere
db = SQLAlchemy()


def init_db(app):
    """Bind SQLAlchemy to the Flask app and create all tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _seed_coins(app)


def _seed_coins(app):
    """Insert coins from coin_list.json if table is empty."""
    import json, os
    from database.models import Coin

    coin_file = os.path.join(os.path.dirname(__file__), "..", "data", "coin_list.json")
    if not os.path.exists(coin_file):
        return

    with open(coin_file) as f:
        data = json.load(f)

    for c in data["coins"]:
        existing = Coin.query.filter_by(symbol=c["symbol"]).first()
        if not existing:
            db.session.add(Coin(symbol=c["symbol"], name=c["name"]))

    db.session.commit()
