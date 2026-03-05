"""
test_scanner.py
Manual test — runs ONE scan cycle and prints results to terminal.
No database required. Great for verifying Binance data + indicators.

Usage:
    python test_scanner.py
    python test_scanner.py BTC 4h
"""

import sys
from scanner.fetch_data import fetch_ohlcv
from scanner.indicators import calculate_indicators
from scanner.signal_detector import detect_signals, compute_composite_score

SYMBOL    = sys.argv[1].upper() if len(sys.argv) > 1 else "BTC"
TIMEFRAME = sys.argv[2]         if len(sys.argv) > 2 else "1h"

print(f"\n🔍 Testing scanner: {SYMBOL} [{TIMEFRAME}]")
print("─" * 45)

# 1. Fetch candles
print("📡 Fetching OHLCV from Binance...")
df = fetch_ohlcv(SYMBOL, interval=TIMEFRAME, limit=100)
if df is None:
    print("❌ Failed to fetch data. Check your internet connection.")
    sys.exit(1)
print(f"✅ Got {len(df)} candles. Latest close: ${df['close'].iloc[-1]:,.4f}")

# 2. Calculate indicators
print("\n📊 Calculating indicators...")
ind = calculate_indicators(df)
if ind is None:
    print("❌ Indicator calculation failed.")
    sys.exit(1)

print(f"  MACD Line:     {ind['macd_line']}")
print(f"  MACD Signal:   {ind['macd_signal']}")
print(f"  EMA 20:        {ind['ema20']}")
print(f"  EMA 50:        {ind['ema50']}")
print(f"  RSI:           {ind['rsi']}")
print(f"  Volume Ratio:  {ind['volume_ratio']}x average")

# 3. Detect signals
print("\n⚡ Detecting signals...")
signals = detect_signals(SYMBOL, TIMEFRAME, ind)

if not signals:
    print("  No signals detected right now.")
else:
    score = compute_composite_score(signals)
    for s in signals:
        emoji = "🟢" if s["direction"] == "bullish" else "🔴" if s["direction"] == "bearish" else "🟡"
        print(f"  {emoji}  {s['signal_type']} ({s['direction']})")
    print(f"\n  📈 Composite Score: {score}")
    if score >= 4:
        print("  🔥 STRONG SETUP — would be saved to database!")

print("\n✅ Test complete.\n")
