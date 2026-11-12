import argparse
import asyncio
import os
import sys
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, os.path.abspath("src"))

import pandas as pd
from indicators import TechnicalIndicators
from market_structure import MarketStructureEngine

from config_loader import ConfigLoader
from realtime_data_engine import RealtimeDataEngine
from realtime_prediction import RealtimePredictionEngine
from prediction_recorder import PredictionRecorder
from paper_trading_engine import PaperTradingEngine
from final_performance_report import FinalPerformanceReporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("XAUUSD-Launcher")

async def run_live_mode(interval: float = 60.0, max_cycles: int = 0):
    logger.info("Initializing XAU/USD Real-Time 60-Second Prediction System...")

    # 1. Initialize prediction engine, recorder, and data engine
    pred_engine = RealtimePredictionEngine(stale_threshold_sec=30.0)
    recorder = PredictionRecorder()
    data_engine = RealtimeDataEngine(symbol="XAUUSD", stale_threshold_sec=30.0)

    # 2. Seed candles from historical clean candles
    clean_candles_path = Path("data/processed/clean_candles.parquet")
    if clean_candles_path.exists():
        try:
            df_candles = pd.read_parquet(clean_candles_path)
            logger.info("Loaded %d historical seed candles.", len(df_candles))
        except Exception as e:
            logger.warning("Could not read clean candles: %s", e)
            df_candles = pd.DataFrame()
    else:
        df_candles = pd.DataFrame()

    latest_tick_data = {"tick": None, "tick_count": 0}

    def on_tick(tick):
        nonlocal df_candles
        latest_tick_data["tick"] = tick
        latest_tick_data["tick_count"] += 1

        # Maintain rolling candle stream (limit to last 300 bars)
        new_row = pd.DataFrame([{
            "timestamp": pd.to_datetime(tick["timestamp"], utc=True),
            "open": tick["bid"],
            "high": tick["ask"],
            "low": tick["bid"],
            "close": tick.get("mid", (tick["bid"] + tick["ask"]) / 2.0),
            "volume": 1.0,
            "tickVolume": 1.0,
            "isOpen": True
        }])
        if not df_candles.empty:
            df_candles = pd.concat([df_candles.tail(300), new_row], ignore_index=True)
        else:
            df_candles = new_row

    data_engine.on_tick_callback = on_tick

    # 3. Start persistent SignalR streaming in background task
    stream_task = asyncio.create_task(data_engine.start_streaming())

    print("\nConnecting to BiQuote SignalR tick stream (https://biquote.io/hubs/tick)...")
    # Wait up to 10 seconds for initial market connection and first tick
    for _ in range(20):
        if latest_tick_data["tick"] is not None and data_engine.connection_status == "CONNECTED":
            break
        await asyncio.sleep(0.5)

    if latest_tick_data["tick"] is None:
        logger.warning("Initial ticks still arriving. Proceeding with scheduler monitoring...")

    # 4. Periodic 60-Second Monotonic Evaluation Loop
    cycle = 0
    next_cycle_time = time.monotonic()

    try:
        while max_cycles == 0 or cycle < max_cycles:
            cycle += 1
            utc_now = datetime.now(timezone.utc)
            local_now = datetime.now().astimezone()
            utc_ts_str = utc_now.isoformat()
            local_ts_str = local_now.strftime("%Y-%m-%d %H:%M:%S %Z")

            # Check model availability
            models_ready = all(
                getattr(pred_engine, m) is not None
                for m in ["dir_model", "calibrator", "eff_model", "touch_model", "time_model"]
            )

            # Check live tick availability & freshness
            current_tick = latest_tick_data["tick"]
            data_ready = False
            rejection_reason_override = None

            if current_tick is not None:
                try:
                    tick_dt = pd.to_datetime(current_tick["timestamp"], utc=True)
                    tick_age = (utc_now - tick_dt).total_seconds()
                    if abs(tick_age) <= 30.0:
                        data_ready = True
                    else:
                        rejection_reason_override = f"DATA BLOCKED: Market data stale (age: {tick_age:.1f}s > 30s)"
                except Exception:
                    rejection_reason_override = "DATA BLOCKED: Malformed tick timestamp"
            else:
                rejection_reason_override = "DATA BLOCKED: No live tick received yet"

            if not models_ready:
                rejection_reason_override = "MODEL BLOCKED: Validated models missing or unverified"

            # Compute features if data & models are ready
            if data_ready and models_ready and not df_candles.empty:
                try:
                    df_ind = TechnicalIndicators.compute_all(df_candles)
                    df_ms = MarketStructureEngine.compute_all(df_ind)
                    df_ms["body_size"] = (df_ms["close"] - df_ms["open"]).abs()
                    df_ms["candle_range"] = df_ms["high"] - df_ms["low"]
                    df_ms["upper_wick"] = df_ms["high"] - df_ms[["open", "close"]].max(axis=1)
                    df_ms["lower_wick"] = df_ms[["open", "close"]].min(axis=1) - df_ms["low"]
                    df_ms["body_ratio"] = df_ms["body_size"] / (df_ms["candle_range"] + 1e-10)
                    latest_features = df_ms.iloc[-1].to_dict()

                    trend_state = int(df_ms.iloc[-1].get("trend_state", 0))
                    market_structure_str = "BULLISH" if trend_state == 1 else ("BEARISH" if trend_state == -1 else "NEUTRAL")
                    market_regime_str = "TRENDING" if abs(trend_state) == 1 else "RANGING"
                    ms_dict = {"invalidated": False, "trend_state": trend_state, "structure": market_structure_str}
                except Exception as fe_err:
                    logger.error("Error computing features: %s", fe_err)
                    latest_features = {}
                    market_regime_str = "UNKNOWN"
                    market_structure_str = "NEUTRAL"
                    ms_dict = {}
            else:
                latest_features = {}
                market_regime_str = "UNKNOWN"
                market_structure_str = "NEUTRAL"
                ms_dict = {}

            # Execute Model Prediction
            if data_ready and models_ready and latest_features:
                res = pred_engine.evaluate_live_tick(current_tick, latest_features, ms_dict)
            else:
                # Blocked state response
                dummy_tick = current_tick or {"symbol": "XAUUSD", "bid": 0.0, "ask": 0.0, "spread": 0.0, "mid": 0.0}
                res = {
                    "timestamp": utc_ts_str,
                    "symbol": "XAUUSD",
                    "direction": "NO_TRADE",
                    "confidence": 0.0,
                    "efficiency": 0.0,
                    "model_version": "v1.0-validated" if models_ready else "UNVERIFIED",
                    "feature_version": "v1.0",
                    "data_timestamp": utc_ts_str,
                    "limit_entry_price": 0.0,
                    "touch_probability": 0.0,
                    "expected_time_to_touch_sec": 0.0,
                    "stop_loss": 0.0,
                    "take_profit": 0.0,
                    "risk_reward": "1:2.0",
                    "validation_status": "REJECTED",
                    "rejection_reasons": [rejection_reason_override or "PREREQUISITES_NOT_MET"]
                }

            # Prepare structured prediction record
            prediction_id = f"PRED-{int(utc_now.timestamp())}-{cycle:03d}"
            signal_expiry_utc = (utc_now + timedelta(seconds=180)).isoformat()
            cur_price = current_tick.get("mid", (current_tick["bid"] + current_tick["ask"]) / 2.0) if current_tick else 0.0

            prediction_record = {
                "prediction_id": prediction_id,
                "utc_timestamp": utc_ts_str,
                "local_timestamp": local_ts_str,
                "symbol": "XAUUSD",
                "current_price": cur_price,
                "bid": current_tick.get("bid", 0.0) if current_tick else 0.0,
                "ask": current_tick.get("ask", 0.0) if current_tick else 0.0,
                "spread": current_tick.get("spread", 0.0) if current_tick else 0.0,
                "market_regime": market_regime_str,
                "market_structure": market_structure_str,
                "direction": res["direction"],
                "confidence": res["confidence"],
                "efficiency": res["efficiency"],
                "limit_entry_price": res["limit_entry_price"],
                "touch_probability": res["touch_probability"],
                "expected_time_to_touch_sec": res["expected_time_to_touch_sec"],
                "stop_loss": res["stop_loss"],
                "take_profit": res["take_profit"],
                "risk_reward": res["risk_reward"],
                "final_decision": res["direction"],
                "validation_status": res["validation_status"],
                "rejection_reasons": res["rejection_reasons"],
                "signal_expiry_utc": signal_expiry_utc,
                "model_version": res.get("model_version", "v1.0-validated"),
                "data_source": "BiQuote SignalR",
                "features": {k: float(v) for k, v in latest_features.items() if isinstance(v, (int, float, bool))}
            }

            # 5. Persist to SQLite and JSON history
            recorder.record_prediction(prediction_record)

            # 6. Render Console Dashboard
            print("\n" + "=" * 56, flush=True)
            print("             XAU/USD 60-SECOND PREDICTION", flush=True)
            print("=" * 56, flush=True)
            print(f"Cycle: {cycle:03d}", flush=True)
            print(f"Prediction Time: {local_ts_str}", flush=True)
            conn_disp = "CONNECTED" if (data_engine.connection_status == "CONNECTED" and data_ready) else (rejection_reason_override or data_engine.connection_status)
            model_disp = "VALIDATED" if models_ready else "MODEL BLOCKED"
            print(f"Market Data: {conn_disp}", flush=True)
            print(f"Model Status: {model_disp}", flush=True)
            print("-" * 56, flush=True)
            if current_tick:
                print(f"Current Price: {cur_price:.3f}", flush=True)
                print(f"Bid: {current_tick['bid']:.3f}", flush=True)
                print(f"Ask: {current_tick['ask']:.3f}", flush=True)
                print(f"Spread: {current_tick['spread']:.3f}", flush=True)
            else:
                print("Current Price: DATA BLOCKED", flush=True)
            print("-" * 56, flush=True)
            print(f"Market Regime: {market_regime_str}", flush=True)
            print(f"Market Structure: {market_structure_str}", flush=True)
            print("-" * 56, flush=True)
            print(f"Direction: {res['direction']}", flush=True)
            print(f"Trade Confidence: {res['confidence']:.2f}% (Threshold: >=90.0%)", flush=True)
            print(f"15-Min Efficiency: {res['efficiency']:.2f}% (Threshold: >=90.0%)", flush=True)

            # Independent Boolean Gate Display
            conf_gate_str = res.get("confidence_gate") or (f"Confidence Gate: PASS ({res['confidence']:.2f} >= 90)" if res['confidence'] >= 90.0 else f"Confidence Gate: FAIL ({res['confidence']:.2f} < 90)")
            eff_gate_str = res.get("efficiency_gate") or (f"Efficiency Gate: PASS ({res['efficiency']:.2f} >= 90)" if res['efficiency'] >= 90.0 else f"Efficiency Gate: FAIL ({res['efficiency']:.2f} < 90)")
            print(f"{conf_gate_str}", flush=True)
            print(f"{eff_gate_str}", flush=True)
            print("-" * 56, flush=True)
            print(f"Limit Entry: {res['limit_entry_price']:.2f}", flush=True)
            print(f"Touch Probability: {res['touch_probability'] * 100:.1f}%", flush=True)
            print(f"Expected Touch Time: {res['expected_time_to_touch_sec']:.1f} seconds", flush=True)
            print("-" * 56, flush=True)
            print(f"Stop Loss: {res['stop_loss']:.2f}", flush=True)
            print(f"Take Profit: {res['take_profit']:.2f}", flush=True)
            print(f"Risk Reward: {res['risk_reward']}", flush=True)
            print("-" * 56, flush=True)
            print(f"Final Decision: {res['direction']}", flush=True)
            if res["rejection_reasons"]:
                print(f"Rejection Reason: {', '.join(res['rejection_reasons'])}", flush=True)
            else:
                print("Status: APPROVED (180s Limit Order Expiry Active)", flush=True)
            print("-" * 56, flush=True)
            print(f"Next Prediction In: {int(interval)} seconds", flush=True)
            print("=" * 56 + "\n", flush=True)

            # 7. Monotonic Timing drift prevention
            next_cycle_time += interval
            sleep_duration = max(0.0, next_cycle_time - time.monotonic())
            if cycle < max_cycles or max_cycles == 0:
                await asyncio.sleep(sleep_duration)

    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Received shutdown signal. Stopping prediction engine...")
    finally:
        data_engine.stop()
        if not stream_task.done():
            stream_task.cancel()
            try:
                await stream_task
            except (asyncio.CancelledError, Exception):
                pass
        logger.info("Real-time 60-second prediction system stopped gracefully.")

def run_preflight_checks():
    logger.info("Executing Preflight System Checks...")
    import pytest
    rc = pytest.main(["-v", "tests/"])
    if rc == 0:
        logger.info("[SUCCESS] All preflight tests passed successfully.")
    else:
        logger.error("[ERROR] Preflight tests failed.")
    return rc

def main():
    parser = argparse.ArgumentParser(description="XAU/USD AI Trading Research & Prediction System Launcher")
    parser.add_argument("--mode", choices=["check", "verify", "live", "paper", "report"], default="check",
                        help="Operation mode: check, verify, live, paper, or report")
    parser.add_argument("--interval", type=float, default=60.0,
                        help="Prediction interval in seconds (default: 60.0)")
    parser.add_argument("--cycles", type=int, default=0,
                        help="Max prediction cycles to run (default: 0 = run indefinitely until Ctrl+C)")
    args = parser.parse_args()

    # Ensure required runtime directories exist
    for dir_name in ["data/processed", "data/raw", "models/trained", "models/validated", "results/verification", "logs"]:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    if args.mode == "check":
        sys.exit(run_preflight_checks())
    elif args.mode == "verify":
        logger.info("Launching Full Independent Verification Suite...")
        import subprocess
        rc = subprocess.call([sys.executable, "tools/run_independent_verification.py"])
        sys.exit(rc)
    elif args.mode == "live" or args.mode == "paper":
        asyncio.run(run_live_mode(interval=args.interval, max_cycles=args.cycles))
    elif args.mode == "report":
        reporter = FinalPerformanceReporter()
        summary = reporter.generate_report()
        logger.info("Final Performance Report Generated:\n%s", summary)

if __name__ == "__main__":
    main()
