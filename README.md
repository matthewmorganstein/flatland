# flatland mvp
## FlatLand Trading Application documentation for the MVP (v1.0)
# Overview

FlatLand is a lightweight trading tool designed for crypto enthusiasts who want to test reversal strategies on Bitcoin (BTC) without the fluff. Built for the solo developer behind LineLand, this MVP backtests the last 15 trades on 30-minute candles, using price data from Twelve Data and mock sentiment indicators (r_1, r_2) until RISE (Real-time Index for Sentiment and Engagement) integration is live. It spits out clear metrics—win rate, profit factor, total profit—and a Plotly chart to see if the strategy holds water. Think of it as a quick, no-nonsense way to spot BTC momentum pivots and decide “worth it or not?” before risking real cash.

# Components
# Lineland Break
Purpose: The core backtesting engine.

Description: Executes trades triggered by Pointland Signal, tracking outcomes over the last 15 BTC trades with a fixed 1-unit position (1 BTC). Measures raw price movement, no leverage or fees.

Trading Context: A reversal strategy that enters when price breaks the previous 30m candle’s high or low, backed by r_1 or r_2 exceeding a threshold.

# Pointland Signal
Purpose: Signal generator for trade entries.

Description: Scans 30m candles for:

Buy Signal: Close < previous low AND (r_1 OR r_2 > Square Threshold).

Sell Signal: Close > previous high AND (r_1 OR r_2 > Square Threshold).

Technical Analysis: r_1 and r_2 are mocked momentum indicators (350-500 range), signaling reversal strength until RISE data is available.

# Square Threshold
Purpose: Filters signals by momentum strength.

Description: A user-set value (default 350) that r_1 or r_2 must exceed to trigger a trade.

Trading Context: Keeps trades focused on strong sentiment shifts, cutting through market noise.

# Sphere Exit
Purpose: Defines trade exits.

Description: Closes trades at a 1% target or stop, or when price hits the opposite extreme (e.g., high after a buy).

Technical Analysis: Simple risk-reward logic for quick backtest results.

# Polygon Profit
Purpose: Delivers performance stats.

Description: Calculates win rate, profit factor, and total profit over the last 15 trades.

Trading Context: A fast check to see if the strategy’s got an edge.

# Tesseract Visual
Purpose: Turns data into visuals.

Description: Plots price and trade outcomes (green for wins, red for losses) in a Plotly chart.

Trading Context: Shows at a glance if the strategy’s winning or tanking.

# Processors
# Flatland Strategy Processor
Purpose: Runs the backtest.

Description: Combines Lineland Break, Pointland Signal, Square Threshold, Sphere Exit, and Polygon Profit into one workflow. Fetches data, finds signals, evaluates trades, and computes metrics.

Endpoint: POST /api/v1/flatland-backtest

Parameters:
symbol (str): "BTC" (fixed for MVP).
start_time (datetime): Start of backtest period.
end_time (datetime): End of backtest period.
threshold (float, optional): Default 350.0.
distance_threshold (float, optional): Default 0.01 (1%).

# Example:
bash
curl -X POST "http://your_server_ip/api/v1/flatland-backtest" \
-H "Content-Type: application/json" \
-H "X-API-Key: your_key" \
-d '{"symbol": "BTC", "start_time": "2025-03-28T00:00:00", "end_time": "2025-03-29T00:00:00"}'

Output: HTML Plotly chart or JSON:
json
{
  "symbol": "BTC",
  "trades": [{"entry_time": "2025-03-28T00:30:00", "entry_price": 60250.0, "exit_price": 60800.0, "profit": 550.0, ...}],
  "performance": {"total_trades": 15, "winning_trades": 9, "profit_factor": 1.8, "win_rate": 0.6, "total_profit": 4500.0}
}

Trading Context: Tests if BTC reversals pay off—quick intel for risk-takers.

# Features
Backtesting: Tests the last 15 BTC trades on 30m data.

Momentum Signals: Uses mock r_1/r_2 (350+ threshold) for reversal triggers.

Simple Metrics: Win rate, profit factor, total profit.

Visual Feedback: Plotly chart of price and trades.

# Concepts
Momentum: Mock r_1/r_2 strength (to be replaced by RISE).

Profit Factor: Gains vs. losses over 15 trades.

Win Rate: Percentage of profitable trades.

# How It Works
Data Pull: Fetches BTC 30m OHLCV from Twelve Data via FlatlandFetcher; mocks r_1/r_2 until RISE is ready.

Signal Check: Pointland Signal scans for breakouts with r_1/r_2 > threshold.

Trade Run: Lineland Break executes and tracks trades.

Exit Logic: Sphere Exit applies 1% target/stop or price reversal.

Results: Polygon Profit computes stats; Tesseract Visual plots it.

# Usage
FlatLand’s your quick shot at testing BTC reversal trades. Load data, run a backtest, and see if it’s worth a swing.

# Example Workflow
Run Backtest:
bash
curl -X POST "http://your_server_ip/api/v1/flatland-backtest" \
-H "Content-Type: application/json" \
-H "X-API-Key: your_key" \
-d '{"symbol": "BTC", "start_time": "2025-03-28T00:00:00", "end_time": "2025-03-29T00:00:00"}'

Output: Get a Plotly chart (open in browser) showing 15 trades (e.g., 9 green wins, 6 red losses) and JSON metrics (e.g., 60% win rate, +4500 profit).

Decide: If it looks solid, dig deeper or share on X for feedback.

# Architecture Flow
Client: Hits /api/v1/flatland-backtest with time range.

FlatlandFetcher: Pulls BTC 30m data from Twelve Data, mocks r_1/r_2.

MongoDB: Stores data in prices collection if not already present.

FlatlandStrategy: Runs backtest, generates trades and metrics.

Tesseract Visual: Renders Plotly HTML.

# Setup
Requirements: Python 3.9+, MongoDB, Twelve Data API key.

Install:
bash
pip install fastapi uvicorn pymongo aiohttp plotly
Env Vars (.env):
MONGO_URI=mongodb://localhost:27017
MONGODB_DB_NAME=lineland
TWELVE_DATA_API_KEY=your_key
API_KEY=your_test_key
PORT=8000

Run:
bash
python app.py

# Testing the DB
To verify it works:

Setup: Connect to your MongoDB instance (local or cloud) via MONGO_URI in settings.py.

Insert Sample Data:

python

from db import MongoDBDAO
from pymongo import MongoClient
from settings import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGODB_DB_NAME]
dao = MongoDBDAO(db)
dao.init_db()
sample_data = [
    {"symbol": "BTC", "time_frame": "30m", "timestamp": "2025-03-28T00:00:00", "open": 60000.0, "high": 60500.0, "low": 59800.0, "close": 60250.0, "volume": 100.0, "r_1": 400.0, "r_2": 350.0}
]
dao.insert_many(sample_data)

Query:

python

data = dao.get_data("BTC", "30m", datetime(2025, 3, 28), datetime(2025, 3, 29))
print(data)

This should store and retrieve the sample candle correctly, ready for backtesting.

# Future Developments (Post-MVP)
RISE Integration: Swap mock r_1/r_2 for real sentiment data.

Real-Time Signals: Add WebSocket endpoint /realtime-signals.

Multi-Symbol: Expand beyond BTC (e.g., ETH).

Threshold Optimization: Introduce ZTestThresholdOptimizationProcessor.

# Conclusion
FlatLand v1.0 is a stripped-down, focused tool for BTC reversal backtesting. It’s quick, visual, and gives crypto traders the raw data they need to act. 
