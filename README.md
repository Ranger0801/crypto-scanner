# ⚡ Crypto Signal Scanner

Automated crypto technical analysis scanner built with Python + Flask.

## Quick Start

```bash
# 1. Clone / enter the project
cd crypto-signal-scanner

# 2. Create virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# 5. Run
python app.py
```

Open http://localhost:5000 — the scanner starts automatically.

## Architecture

```
Binance API  ──┐
               ├→ fetch_data.py → indicators.py → signal_detector.py → PostgreSQL
CoinGecko API ─┘                                                          ↓
                                                                    Flask API
                                                                          ↓
                                                                    Frontend Dashboard
```

## Detected Signals

| Signal         | Score |
|----------------|-------|
| MACD Bullish   | +2    |
| MACD Bearish   | +2    |
| EMA Bullish    | +2    |
| EMA Bearish    | +2    |
| Volume Spike   | +1    |
| RSI Oversold   | +1    |
| RSI Overbought | +1    |

Score ≥ 4 = Strong setup 🔥

## API Endpoints

| Endpoint                | Description                        |
|-------------------------|------------------------------------|
| `GET /api/signals`      | Latest signals (filterable)        |
| `GET /api/strong_signals` | Signals with score ≥ 4           |
| `GET /api/top_gainers`  | Top 10 coins by 24h gain           |
| `GET /api/top_losers`   | Top 10 coins by 24h loss           |
| `GET /api/coin/<symbol>`| Coin detail + recent signals       |
| `GET /api/market_overview` | Aggregate signal stats          |
| `GET /api/health`       | Health check                       |

## Deployment

| Component      | Platform          |
|----------------|-------------------|
| Frontend       | Vercel            |
| Backend API    | Render            |
| Database       | Supabase/PostgreSQL |
| Scanner Worker | Render background |
