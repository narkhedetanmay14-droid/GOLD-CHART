import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from model_registry import ModelRegistry
from prediction_validator import PredictionValidator
from limit_entry_engine import LimitEntryEngine

logger = logging.getLogger(__name__)

class RealtimePredictionEngine:
    """Production-grade real-time prediction pipeline using verified, calibrated models:
    - Direction Classifier: Multi-class Random Forest
    - Trade Confidence: Calibrated probability of TP hit before SL
    - 15-Minute Efficiency: HistGradientBoosting regressor forecasting favourable excursion
    - Limit Entry: Structure-aware price, Touch Probability model, and Time-to-Touch model
    - Strict 90/90 Gates: Confidence >= 90.0 and Efficiency >= 90.0 required for BUY/SELL
    - Strict Schema Validation: Rejects missing features (never silently filled with zero).
    """

    def __init__(
        self,
        models_dir: str = "models",
        confidence_threshold: float = 90.0,
        efficiency_threshold: float = 90.0,
        stale_threshold_sec: float = 15.0
    ):
        self.models_dir = models_dir
        self.confidence_threshold = confidence_threshold
        self.efficiency_threshold = efficiency_threshold
        self.stale_threshold_sec = stale_threshold_sec
        self.registry = ModelRegistry(models_dir=models_dir)

        # Preload validated models
        self.dir_model = self._load_model_safe("direction_classifier")
        self.calibrator = self._load_model_safe("confidence_calibrator")
        self.eff_model = self._load_model_safe("efficiency_forecaster")
        self.touch_model = self._load_model_safe("limit_touch_model")
        self.time_model = self._load_model_safe("limit_time_model")

    def _load_model_safe(self, model_name: str) -> Optional[Any]:
        try:
            return self.registry.load_model(model_name, stage="validated")
        except Exception:
            try:
                return self.registry.load_model(model_name, stage="trained")
            except Exception as e:
                logger.warning("Could not load model %s: %s", model_name, e)
                return None

    def evaluate_live_tick(
        self,
        tick: Dict[str, Any],
        features: Dict[str, Any],
        market_structure: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute complete prediction pipeline on live tick and feature vector."""
        timestamp_str = tick.get("timestamp") or datetime.now(timezone.utc).isoformat()
        symbol = str(tick.get("symbol", "XAUUSD")).replace("/", "")
        bid = float(tick.get("bid", 0.0))
        ask = float(tick.get("ask", 0.0))
        spread = ask - bid if ask > bid else 0.0

        rejection_reasons = []

        # 1. Market data freshness & sanity validation
        if bid <= 0 or ask <= 0 or bid >= ask:
            rejection_reasons.append("INVALID_BID_ASK")
        if spread > 10.0:
            rejection_reasons.append("EXCESSIVE_SPREAD")

        try:
            tick_dt = pd.to_datetime(timestamp_str, utc=True)
            age = (datetime.now(timezone.utc) - tick_dt).total_seconds()
            if abs(age) > self.stale_threshold_sec:
                rejection_reasons.append(f"STALE_MARKET_DATA (age {age:.1f}s > {self.stale_threshold_sec}s)")
        except Exception:
            rejection_reasons.append("MALFORMED_TIMESTAMP")

        # 2. Market structure invalidation
        ms = market_structure or {}
        if ms.get("invalidated", False):
            rejection_reasons.append("INVALID_MARKET_STRUCTURE")

        # 3. Model availability check
        model_errors = []
        if self.dir_model is None:
            model_errors.append("DIRECTION MODEL BLOCKED")
        if self.calibrator is None:
            model_errors.append("CONFIDENCE CALIBRATOR BLOCKED")
        if self.eff_model is None:
            model_errors.append("EFFICIENCY MODEL BLOCKED")
        if self.touch_model is None or self.time_model is None:
            model_errors.append("LIMIT MODEL BLOCKED")

        if model_errors:
            rejection_reasons.extend(model_errors)

        # 4. Strict Feature Schema Validation (Never fill missing features with zero)
        if not features or not isinstance(features, dict):
            rejection_reasons.append("MISSING_FEATURES")
            expected_features = []
        else:
            expected_features = getattr(self.dir_model, "feature_names_in_", None)
            if expected_features is not None:
                missing_feats = [f for f in expected_features if f not in features]
                if missing_feats:
                    rejection_reasons.append(f"INCOMPATIBLE_FEATURE_SCHEMA: Missing {len(missing_feats)} features: {missing_feats[:3]}...")

        # If any preliminary checks fail, reject immediately with NO_TRADE
        if rejection_reasons:
            return self._build_no_trade_response(
                symbol, timestamp_str, bid, ask, spread, rejection_reasons
            )

        # 5. Assemble exact feature vector
        X_df = pd.DataFrame([features])[expected_features]

        # 6. Model Prediction: Direction
        pred_label = self.dir_model.predict(X_df)[0]
        raw_probs = self.dir_model.predict_proba(X_df)[0]
        raw_max_prob = float(np.max(raw_probs))

        if pred_label == 1:
            raw_direction = "BUY"
        elif pred_label == -1:
            raw_direction = "SELL"
        else:
            raw_direction = "NO_TRADE"

        # 7. Model-Driven Calibrated Trade Confidence (Probability of TP before SL)
        if self.calibrator is not None:
            calibrated_prob = float(self.calibrator.predict_proba(np.array([raw_max_prob]))[0])
            trade_confidence = float(np.clip(calibrated_prob * 100.0, 0.0, 100.0))
        else:
            trade_confidence = 0.0
            rejection_reasons.append("CONFIDENCE CALIBRATOR BLOCKED")

        # 8. Model-Driven 15-Minute Efficiency Forecast (0-100 score)
        if self.eff_model is not None:
            eff_pred = float(self.eff_model.predict(X_df)[0])
            trade_efficiency = float(np.clip(eff_pred, 0.0, 100.0))
        else:
            trade_efficiency = 0.0
            rejection_reasons.append("EFFICIENCY MODEL BLOCKED")

        # 9. Model-Driven Limit Entry, Touch Probability, and Time-to-Touch
        atr = float(features.get("atr_14", 2.0))
        mid = (bid + ask) / 2.0
        limit_price = LimitEntryEngine.calculate_limit_price(
            current_price=mid,
            atr=atr,
            direction=raw_direction,
            pullback_pct=0.3,
            bid=bid,
            ask=ask,
            market_structure=ms
        )

        if self.touch_model is not None and hasattr(self.touch_model, "predict_proba"):
            touch_prob = float(self.touch_model.predict_proba(X_df)[0][1])
        else:
            touch_prob = 0.0
            rejection_reasons.append("LIMIT MODEL BLOCKED")

        if self.time_model is not None:
            expected_time_sec = float(self.time_model.predict(X_df)[0])
        else:
            expected_time_sec = 0.0
            rejection_reasons.append("LIMIT MODEL BLOCKED")

        # 10. Risk / Reward Calculation (Strictly 1:2)
        r_dist = max(atr * 1.5, 2.0)
        if raw_direction == "BUY":
            stop_loss = round(limit_price - r_dist, 2)
            take_profit = round(limit_price + (2.0 * r_dist), 2)
        elif raw_direction == "SELL":
            stop_loss = round(limit_price + r_dist, 2)
            take_profit = round(limit_price - (2.0 * r_dist), 2)
        else:
            stop_loss = round(mid - r_dist, 2)
            take_profit = round(mid + (2.0 * r_dist), 2)

        risk = abs(limit_price - stop_loss)
        reward = abs(take_profit - limit_price)
        rr_ratio = reward / risk if risk > 0 else 2.0

        # 11. Strict 90/90 Gate Enforcement
        validation = PredictionValidator.validate_signal(
            confidence_score=trade_confidence,
            efficiency_score=trade_efficiency,
            direction=raw_direction
        )

        can_trade = validation.get("can_trade", False)
        if not can_trade:
            final_direction = "NO_TRADE"
            for r in validation.get("reasons", []):
                rejection_reasons.append(r)
        else:
            final_direction = raw_direction

        return {
            "timestamp": str(timestamp_str),
            "symbol": symbol,
            "direction": final_direction,
            "confidence": round(trade_confidence, 2),
            "efficiency": round(trade_efficiency, 2),
            "confidence_gate": validation.get("confidence_gate"),
            "efficiency_gate": validation.get("efficiency_gate"),
            "model_version": "v1.0-validated",
            "feature_version": "v1.0",
            "data_timestamp": str(timestamp_str),
            "limit_entry_price": round(limit_price, 2),
            "touch_probability": round(touch_prob, 4),
            "expected_time_to_touch_sec": round(expected_time_sec, 1),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward": f"1:{rr_ratio:.1f}",
            "validation_status": "APPROVED" if can_trade else "REJECTED",
            "rejection_reasons": rejection_reasons
        }

    def _build_no_trade_response(
        self, symbol: str, timestamp_str: str, bid: float, ask: float, spread: float, reasons: list
    ) -> Dict[str, Any]:
        mid = (bid + ask) / 2.0 if ask > 0 else 0.0
        return {
            "timestamp": str(timestamp_str),
            "symbol": symbol,
            "direction": "NO_TRADE",
            "confidence": 0.0,
            "efficiency": 0.0,
            "model_version": "v1.0-validated",
            "feature_version": "v1.0",
            "data_timestamp": str(timestamp_str),
            "limit_entry_price": round(mid, 2),
            "touch_probability": 0.0,
            "expected_time_to_touch_sec": 0.0,
            "stop_loss": round(mid - 10.0, 2),
            "take_profit": round(mid + 20.0, 2),
            "risk_reward": "1:2.0",
            "validation_status": "REJECTED",
            "rejection_reasons": reasons
        }
