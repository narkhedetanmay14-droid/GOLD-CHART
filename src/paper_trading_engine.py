import time
import uuid
from typing import Dict, Any, List, Optional
import pandas as pd

from json_logger import JsonLogger
from risk_manager import RiskManager

class PaperTradingEngine:
    """Simulates paper trading with 180-second limit order expiry, position tracking, and JSON persistence."""

    def __init__(self, initial_balance: float = 100000.0, data_dir: str = "data"):
        self.balance = initial_balance
        self.equity = initial_balance
        self.pending_orders: List[Dict[str, Any]] = []
        self.open_positions: List[Dict[str, Any]] = []
        self.trade_history: List[Dict[str, Any]] = []
        self.expired_signals: List[Dict[str, Any]] = []
        self.invalidated_signals: List[Dict[str, Any]] = []
        self.signal_audit: List[Dict[str, Any]] = []
        self.logger = JsonLogger(data_dir=data_dir)
        self.risk_manager = RiskManager()

    def submit_limit_signal(
        self,
        symbol: str,
        direction: str,
        limit_price: float,
        stop_loss: float,
        take_profit: float,
        confidence: float,
        efficiency: float,
        model_version: str = "v1.0"
    ) -> Dict[str, Any]:
        signal_id = str(uuid.uuid4())
        audit_entry = {
            "signal_id": signal_id,
            "timestamp": pd.Timestamp.utcnow().isoformat(),
            "symbol": symbol,
            "direction": direction,
            "limit_price": limit_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "confidence": confidence,
            "efficiency": efficiency,
            "model_version": model_version
        }
        self.signal_audit.append(audit_entry)

        # Risk check
        risk_check = self.risk_manager.validate_trade_risk(
            limit_price, stop_loss, take_profit, confidence, efficiency
        )
        if not risk_check["approved"]:
            audit_entry["status"] = "REJECTED_BY_RISK"
            audit_entry["reason"] = risk_check["reason"]
            self.invalidated_signals.append(audit_entry)
            self._save_state()
            return {"status": "REJECTED", "reason": risk_check["reason"]}

        order = {
            "order_id": signal_id,
            "symbol": symbol,
            "direction": direction,
            "limit_price": limit_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "placed_at": time.time(),
            "expires_at": time.time() + 180.0,  # 180s expiry
            "status": "PENDING"
        }
        self.pending_orders.append(order)
        self._save_state()
        return {"status": "SUBMITTED", "order_id": signal_id}

    def on_market_tick(self, bid: float, ask: float):
        current_time = time.time()
        # 1. Check pending orders for touch/fill or expiry
        remaining_pending = []
        for order in self.pending_orders:
            if current_time >= order["expires_at"]:
                # Expired - cancel, do not chase!
                order["status"] = "EXPIRED"
                order["reason"] = "180s_timeout_no_touch"
                self.expired_signals.append(order)
                continue

            # Check fill
            filled = False
            fill_price = None
            if order["direction"] == "BUY" and ask <= order["limit_price"]:
                filled = True
                fill_price = ask
            elif order["direction"] == "SELL" and bid >= order["limit_price"]:
                filled = True
                fill_price = bid

            if filled:
                position = {
                    "position_id": order["order_id"],
                    "direction": order["direction"],
                    "entry_price": fill_price,
                    "stop_loss": order["stop_loss"],
                    "take_profit": order["take_profit"],
                    "opened_at": current_time
                }
                self.open_positions.append(position)
            else:
                remaining_pending.append(order)
        self.pending_orders = remaining_pending

        # 2. Check open positions for SL/TP exit
        remaining_positions = []
        for pos in self.open_positions:
            closed = False
            exit_price = None
            outcome = None

            if pos["direction"] == "BUY":
                if bid >= pos["take_profit"]:
                    closed = True
                    exit_price = pos["take_profit"]
                    outcome = "WIN"
                elif bid <= pos["stop_loss"]:
                    closed = True
                    exit_price = pos["stop_loss"]
                    outcome = "LOSS"
            elif pos["direction"] == "SELL":
                if ask <= pos["take_profit"]:
                    closed = True
                    exit_price = pos["take_profit"]
                    outcome = "WIN"
                elif ask >= pos["stop_loss"]:
                    closed = True
                    exit_price = pos["stop_loss"]
                    outcome = "LOSS"

            if closed:
                pnl = (exit_price - pos["entry_price"]) if pos["direction"] == "BUY" else (pos["entry_price"] - exit_price)
                self.balance += pnl
                trade_record = {
                    **pos,
                    "exit_price": exit_price,
                    "outcome": outcome,
                    "pnl": pnl,
                    "closed_at": current_time
                }
                self.trade_history.append(trade_record)
            else:
                remaining_positions.append(pos)
        self.open_positions = remaining_positions
        self._save_state()

    def _save_state(self):
        self.logger.write_json("upcoming_signals.json", self.pending_orders)
        self.logger.write_json("trade_history.json", self.trade_history)
        self.logger.write_json("winning_trades.json", [t for t in self.trade_history if t.get("outcome") == "WIN"])
        self.logger.write_json("failed_trades.json", [t for t in self.trade_history if t.get("outcome") == "LOSS"])
        self.logger.write_json("expired_signals.json", self.expired_signals)
        self.logger.write_json("invalidated_signals.json", self.invalidated_signals)
        self.logger.write_json("signal_audit.json", self.signal_audit)
