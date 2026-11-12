import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from json_logger import JsonLogger

logger = logging.getLogger(__name__)

class PredictionRecorder:
    """Manages persistent SQLite storage and atomic JSON exports for all 60-second predictions.
    Tracks prediction history, active signals, and 180-second limit expirations.
    """

    def __init__(self, data_dir: str = "data", db_name: str = "predictions.db"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / db_name
        self.json_logger = JsonLogger(data_dir=str(self.data_dir))
        self.history_json_file = "prediction_history.json"
        self.active_signals_file = "active_signals.json"
        self._init_sqlite()

    def _init_sqlite(self) -> None:
        """Initialize the SQLite schema for recording all predictions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    prediction_id TEXT PRIMARY KEY,
                    utc_timestamp TEXT NOT NULL,
                    local_timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    current_price REAL NOT NULL,
                    bid REAL NOT NULL,
                    ask REAL NOT NULL,
                    spread REAL NOT NULL,
                    market_regime TEXT,
                    market_structure TEXT,
                    direction TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    efficiency REAL NOT NULL,
                    limit_entry_price REAL NOT NULL,
                    touch_probability REAL NOT NULL,
                    expected_time_to_touch_sec REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    take_profit REAL NOT NULL,
                    risk_reward TEXT NOT NULL,
                    final_decision TEXT NOT NULL,
                    validation_status TEXT NOT NULL,
                    rejection_reasons TEXT,
                    signal_expiry_utc TEXT NOT NULL,
                    model_version TEXT,
                    data_source TEXT,
                    features_json TEXT
                )
            """)
            conn.commit()

    def record_prediction(self, record: Dict[str, Any]) -> None:
        """Store prediction in SQLite database and append to atomic JSON history."""
        # 1. Insert into SQLite
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO predictions (
                        prediction_id, utc_timestamp, local_timestamp, symbol,
                        current_price, bid, ask, spread, market_regime, market_structure,
                        direction, confidence, efficiency, limit_entry_price,
                        touch_probability, expected_time_to_touch_sec, stop_loss,
                        take_profit, risk_reward, final_decision, validation_status,
                        rejection_reasons, signal_expiry_utc, model_version,
                        data_source, features_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record["prediction_id"],
                    record["utc_timestamp"],
                    record["local_timestamp"],
                    record["symbol"],
                    float(record.get("current_price", 0.0)),
                    float(record.get("bid", 0.0)),
                    float(record.get("ask", 0.0)),
                    float(record.get("spread", 0.0)),
                    str(record.get("market_regime", "UNKNOWN")),
                    str(record.get("market_structure", "NEUTRAL")),
                    str(record.get("direction", "NO_TRADE")),
                    float(record.get("confidence", 0.0)),
                    float(record.get("efficiency", 0.0)),
                    float(record.get("limit_entry_price", 0.0)),
                    float(record.get("touch_probability", 0.0)),
                    float(record.get("expected_time_to_touch_sec", 0.0)),
                    float(record.get("stop_loss", 0.0)),
                    float(record.get("take_profit", 0.0)),
                    str(record.get("risk_reward", "1:2.0")),
                    str(record.get("final_decision", "NO_TRADE")),
                    str(record.get("validation_status", "REJECTED")),
                    json.dumps(record.get("rejection_reasons", [])),
                    record["signal_expiry_utc"],
                    str(record.get("model_version", "v1.0-validated")),
                    str(record.get("data_source", "BiQuote SignalR")),
                    json.dumps(record.get("features", {}))
                ))
                conn.commit()
        except Exception as e:
            logger.error("Failed to write prediction to SQLite: %s", e)

        # 2. Append to JSON history atomically
        try:
            existing = self.json_logger.read_json(self.history_json_file)
            if not isinstance(existing, list):
                existing = []
            # Keep clean summary in JSON list
            clean_record = {k: v for k, v in record.items() if k != "features"}
            existing.append(clean_record)
            self.json_logger.write_json(self.history_json_file, existing)
        except Exception as e:
            logger.error("Failed to append prediction to JSON history: %s", e)

        # 3. Track active signal if approved (BUY / SELL) and expire old ones
        self._manage_active_signals(record)

    def _manage_active_signals(self, new_record: Dict[str, Any]) -> None:
        """Expire unfilled orders older than 180 seconds and manage new approved signals."""
        now = datetime.now(timezone.utc)
        active_list = self.json_logger.read_json(self.active_signals_file)
        if not isinstance(active_list, list):
            active_list = []

        unexpired = []
        for sig in active_list:
            expiry_str = sig.get("signal_expiry_utc")
            try:
                exp_dt = datetime.fromisoformat(expiry_str)
                if now < exp_dt:
                    unexpired.append(sig)
                else:
                    logger.info("Signal %s EXPIRED (>180s unfilled). Cancelling.", sig.get("prediction_id"))
            except Exception:
                pass

        # If current prediction was an approved BUY/SELL trade
        if new_record.get("final_decision") in ["BUY", "SELL"] and new_record.get("validation_status") == "APPROVED":
            # Duplicate prevention: avoid inserting duplicate signal for same setup/direction
            is_dup = any(s.get("direction") == new_record.get("direction") for s in unexpired)
            if not is_dup:
                unexpired.append({
                    "prediction_id": new_record["prediction_id"],
                    "direction": new_record["direction"],
                    "limit_entry_price": new_record["limit_entry_price"],
                    "stop_loss": new_record["stop_loss"],
                    "take_profit": new_record["take_profit"],
                    "created_at_utc": new_record["utc_timestamp"],
                    "signal_expiry_utc": new_record["signal_expiry_utc"]
                })

        self.json_logger.write_json(self.active_signals_file, unexpired)

    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch the most recent predictions from SQLite."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM predictions ORDER BY rowid DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error("Error reading recent predictions: %s", e)
            return []
