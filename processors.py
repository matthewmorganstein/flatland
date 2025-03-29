from typing import List, Dict, Any
import logging
from datetime import datetime
from db import MongoDBDAO
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

class FlatlandStrategy:
    def __init__(self, dao: MongoDBDAO, symbol: str = "BTC", threshold: float = 350.0):
        self.dao = dao
        self.symbol = symbol
        self.threshold = threshold
        self.position_size = 1  # Fixed at 1 BTC
        self.trades = []
        self.signal_limit = 15

    def determine_signal_direction(self, current: Dict[str, float], previous: Dict[str, float]) -> str:
        """Assign buy/sell based on breakout."""
        if current["close"] < previous["low"]:
            return "buy"
        elif current["close"] > previous["high"]:
            return "sell"
        return None

    def evaluate_trade_success(
        self, entry_data: Dict[str, float], data: List[Dict[str, float]], entry_idx: int, distance_threshold: float = 0.01
    ) -> Dict[str, Any]:
        entry_price = entry_data["close"]
        signal_high = entry_data["high"]
        signal_low = entry_data["low"]
        direction = entry_data["signal_type"]

        target = signal_high * (1 + distance_threshold) if direction == "buy" else signal_low * (1 - distance_threshold)
        stop = signal_low * (1 - distance_threshold) if direction == "buy" else signal_high * (1 + distance_threshold)

        exit_price = None
        exit_time = None
        success = False
        failure = False

        for i in range(entry_idx + 1, len(data)):
            current = data[i]
            current_price = current["close"]
            if (direction == "buy" and current_price <= stop) or (direction == "sell" and current_price >= stop):
                exit_price = current_price
                exit_time = current["timestamp"]
                failure = True
                break
            if current_price >= target if direction == "buy" else current_price <= target:
                exit_price = current_price
                exit_time = current["timestamp"]
                success = True
                break

        if not exit_price and entry_idx < len(data) - 1:
            exit_price = data[-1]["close"]
            exit_time = data[-1]["timestamp"]
            failure = (direction == "buy" and exit_price <= stop) or (direction == "sell" and exit_price >= stop)

        profit = (exit_price - entry_price) if direction == "buy" else (entry_price - exit_price)
        return {"success": success, "failure": failure, "profit": profit, "exit_price": exit_price, "exit_time": exit_time}

    def backtest_last_signals(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        data = self.dao.get_data(self.symbol, "30m", start_time, end_time)
        if len(data) < 2:
            raise ValueError("Insufficient data for backtesting")

        signals = []
        for i in range(1, len(data)):
            current = data[i]
            previous = data[i - 1]
            if (current["r_1"] > self.threshold or current["r_2"] > self.threshold):
                direction = self.determine_signal_direction(current, previous)
                if direction:
                    current["signal_type"] = direction
                    signals.append((i, current))
            if len(signals) >= self.signal_limit:
                break

        if not signals:
            raise ValueError("No signals found")

        self.trades = []
        for signal_idx, signal in signals[-self.signal_limit:]:
            result = self.evaluate_trade_success(signal, data, signal_idx)
            trade = {
                "entry_time": signal["timestamp"],
                "entry_price": signal["close"],
                "exit_time": result["exit_time"],
                "exit_price": result["exit_price"],
                "direction": signal["signal_type"].upper(),
                "r_1": signal["r_1"],
                "r_2": signal["r_2"],
                "profit": result["profit"],
                "success": result["success"],
                "failure": result["failure"]
            }
            self.trades.append(trade)

        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t["profit"] > 0])
        total_profit = sum(t["profit"] for t in self.trades if t["profit"] > 0)
        total_loss = abs(sum(t["profit"] for t in self.trades if t["profit"] < 0))
        profit_factor = total_profit / total_loss if total_loss > 0 else float("inf")
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        return {
            "symbol": self.symbol,
            "trades": self.trades,
            "performance": {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "profit_factor": profit_factor,
                "win_rate": win_rate,
                "total_profit": total_profit - total_loss,
                "threshold": self.threshold
            }
        }

    def visualize_trades(self) -> str:
        if not self.trades:
            logger.warning("No trades to visualize")
            return ""

        fig = go.Figure()
        for trade in self.trades:
            color = "green" if trade["profit"] > 0 else "red"
            fig.add_trace(go.Scatter(
                x=[trade["entry_time"], trade["exit_time"]],
                y=[trade["entry_price"], trade["exit_price"]],
                mode="lines+markers",
                line=dict(color=color),
                name=f"{trade['direction']} ({trade['profit']:.2f})",
                hoverinfo="text",
                text=[
                    f"Entry: {trade['entry_price']}<br>R_1: {trade['r_1']}<br>R_2: {trade['r_2']}",
                    f"Exit: {trade['exit_price']}<br>Profit: {trade['profit']:.2f}"
                ]
            ))

        fig.update_layout(
            title=f"Flatland Backtest for {self.symbol} (Last {self.signal_limit} 30m Signals)",
            xaxis_title="Time",
            yaxis_title="Price",
            template="plotly_dark"
        )
        return fig.to_html(full_html=False)

def get_flatland_strategy(dao: MongoDBDAO):
    from settings import settings
    return FlatlandStrategy(dao, threshold=350.0)
