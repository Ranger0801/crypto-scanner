from datetime import datetime
from database.db import db


class Coin(db.Model):
    """Stores the latest market snapshot for each coin."""
    __tablename__ = "coins"

    id          = db.Column(db.Integer, primary_key=True)
    symbol      = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name        = db.Column(db.String(100), nullable=False)
    price       = db.Column(db.Float, nullable=True)
    volume_24h  = db.Column(db.Float, nullable=True)
    change_24h  = db.Column(db.Float, nullable=True)   # percent
    market_cap  = db.Column(db.Float, nullable=True)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    signals = db.relationship("Signal", backref="coin_ref", lazy="dynamic")

    def to_dict(self):
        return {
            "symbol":     self.symbol,
            "name":       self.name,
            "price":      self.price,
            "volume_24h": self.volume_24h,
            "change_24h": self.change_24h,
            "market_cap": self.market_cap,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Signal(db.Model):
    """Stores every detected trading signal."""
    __tablename__ = "signals"

    id          = db.Column(db.Integer, primary_key=True)
    coin_symbol = db.Column(db.String(20), db.ForeignKey("coins.symbol"), nullable=False, index=True)
    signal_type = db.Column(db.String(50), nullable=False)   # e.g. "MACD Bullish"
    direction   = db.Column(db.String(10), nullable=False)   # "bullish" | "bearish"
    timeframe   = db.Column(db.String(10), nullable=False)   # "1h" | "4h" | "1d"
    score       = db.Column(db.Integer, default=0)
    details     = db.Column(db.Text, nullable=True)          # JSON string with indicator values
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "coin":        self.coin_symbol,
            "signal_type": self.signal_type,
            "direction":   self.direction,
            "timeframe":   self.timeframe,
            "score":       self.score,
            "details":     self.details,
            "timestamp":   self.timestamp.isoformat(),
        }
