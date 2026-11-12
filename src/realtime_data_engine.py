import asyncio
import logging
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
import pandas as pd
from pysignalr.client import SignalRClient
from data_validator import DataValidator
from candle_builder import CandleBuilder

logger = logging.getLogger(__name__)

class RealtimeDataEngine:
    """Robust BiQuote SignalR streaming client for XAU/USD real-time ticks.
    Connects to https://biquote.io/hubs/tick, subscribes to XAUUSD, handles ReceiveTick,
    performs real-time validation, duplicate filtering, incremental candle building, and persistence.
    """

    def __init__(
        self,
        symbol: str = "XAUUSD",
        hub_url: str = "https://biquote.io/hubs/tick",
        stale_threshold_sec: float = 15.0,
        max_cache_size: int = 10000,
        on_tick_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.symbol = symbol.replace("/", "")
        self.hub_url = hub_url
        self.stale_threshold_sec = stale_threshold_sec
        self.max_cache_size = max_cache_size
        self.on_tick_callback = on_tick_callback

        self.validator = DataValidator()
        self.candle_builder = CandleBuilder()
        self.client: Optional[SignalRClient] = None
        self.run_task: Optional[asyncio.Task] = None
        self.running = False

        # Bounded duplicate cache with deterministic FIFO eviction
        self.seen_ticks: OrderedDict = OrderedDict()

        self.received_ticks: List[Dict[str, Any]] = []
        self.connection_logs: List[Dict[str, Any]] = []
        self.last_tick_time = 0.0
        self.connection_status = "DISCONNECTED"

        self.tick_count = 0
        self.duplicate_count = 0
        self.rejected_count = 0
        self.error_count = 0
        self.disconnect_count = 0
        self.first_tick_time: Optional[str] = None
        self.last_tick_timestamp: Optional[str] = None

    def _log_connection(self, event: str, details: str = "") -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "status": self.connection_status,
            "details": details
        }
        self.connection_logs.append(entry)
        logger.info("[ConnectionLog] %s: %s (Status: %s)", event, details, self.connection_status)

    async def handle_receive_tick(self, arguments: list) -> None:
        """Handle incoming 'ReceiveTick' event from BiQuote SignalR hub.
        Official format: arguments is a list where arguments[0] is the tick dict.
        """
        try:
            if not arguments or not isinstance(arguments[0], dict):
                self.rejected_count += 1
                return

            tick = arguments[0]
            tick_symbol = str(tick.get("symbol", "")).replace("/", "")
            if tick_symbol and tick_symbol != self.symbol:
                self.rejected_count += 1
                return

            # Validate bid / ask
            bid = float(tick.get("bid", 0.0))
            ask = float(tick.get("ask", 0.0))
            if bid <= 0 or ask <= 0 or bid >= ask:
                self.rejected_count += 1
                logger.warning("Rejected tick due to invalid bid/ask: bid=%s, ask=%s", bid, ask)
                return

            spread = ask - bid
            if spread > 10.0:  # Excessive spread guardrail for gold
                self.rejected_count += 1
                logger.warning("Rejected tick due to excessive spread: %s", spread)
                return

            # Timestamp validation
            ts_str = tick.get("timestamp") or tick.get("time")
            if not ts_str:
                self.rejected_count += 1
                logger.warning("Rejected tick due to missing timestamp")
                return

            try:
                dt = pd.to_datetime(ts_str, utc=True)
            except Exception:
                self.rejected_count += 1
                logger.warning("Rejected tick due to malformed timestamp: %s", ts_str)
                return

            now = datetime.now(timezone.utc)
            age = (now - dt).total_seconds()
            if abs(age) > self.stale_threshold_sec:
                self.rejected_count += 1
                logger.warning("Rejected stale tick (age: %.2fs)", age)
                return
            if age < -5.0:  # Future-dated tick rejection
                self.rejected_count += 1
                logger.warning("Rejected future-dated tick (ahead by %.2fs)", -age)
                return

            # Duplicate check via signature (timestamp, bid, ask)
            sig = (str(dt), bid, ask)
            if sig in self.seen_ticks:
                self.duplicate_count += 1
                return

            # Insert into bounded FIFO cache
            self.seen_ticks[sig] = True
            if len(self.seen_ticks) > self.max_cache_size:
                self.seen_ticks.popitem(last=False)

            self.tick_count += 1
            self.last_tick_time = time.time()
            iso_time = dt.isoformat()
            if not self.first_tick_time:
                self.first_tick_time = iso_time
            self.last_tick_timestamp = iso_time

            tick_record = {
                "symbol": self.symbol,
                "bid": bid,
                "ask": ask,
                "mid": tick.get("mid", (bid + ask) / 2.0),
                "spread": spread,
                "timestamp": iso_time,
                "source": tick.get("source", "BiQuote SignalR")
            }

            # Keep a bounded list of recent ticks in memory
            if len(self.received_ticks) >= 1000:
                self.received_ticks.pop(0)
            self.received_ticks.append(tick_record)

            # Update candle builder
            try:
                self.candle_builder.update(bid, ask, dt)
            except Exception:
                pass

            # Dispatch callback if registered
            if self.on_tick_callback:
                try:
                    self.on_tick_callback(tick_record)
                except Exception as cb_err:
                    logger.error("Callback error: %s", cb_err)

            logger.info("Accepted live tick #%d: bid=%.3f ask=%.3f spread=%.3f ts=%s", self.tick_count, bid, ask, spread, iso_time)

        except Exception as e:
            self.error_count += 1
            logger.error("Error processing tick: %s", e)

    async def handle_subscription_state(self, arguments: list) -> None:
        """Handle server acknowledgement of symbol subscription."""
        logger.info("Subscription confirmed for symbol: %s (State: %s)", self.symbol, arguments)

    async def start_streaming(self, duration: Optional[float] = None) -> None:
        """Start persistent SignalR streaming with auto-reconnection and resubscription."""
        self.running = True
        self.connection_status = "CONNECTING"
        self._log_connection("START_STREAMING", f"Connecting to {self.hub_url}")

        backoff = 1.0
        while self.running:
            try:
                self.client = SignalRClient(self.hub_url)
                self.client.on("ReceiveTick", self.handle_receive_tick)
                self.client.on("ReceiveSubscriptionState", self.handle_subscription_state)

                async def on_open():
                    self.connection_status = "CONNECTED"
                    self._log_connection("CONNECTED", f"Subscribing to [[\"{self.symbol}\"]]")
                    await self.client.send("Subscribe", [[self.symbol]])

                async def on_close():
                    self.disconnect_count += 1
                    self.connection_status = "DISCONNECTED"
                    self._log_connection("ON_CLOSE", "Connection closed by server.")

                self.client.on_open(on_open)
                self.client.on_close(on_close)

                self.run_task = asyncio.create_task(self.client.run())

                if duration:
                    await asyncio.sleep(duration)
                    self.running = False
                    if self.run_task and not self.run_task.done():
                        self.run_task.cancel()
                        try:
                            await self.run_task
                        except (asyncio.CancelledError, Exception):
                            pass
                    break
                else:
                    await self.run_task

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.error_count += 1
                self.disconnect_count += 1
                self.connection_status = "RECONNECTING"
                self._log_connection("DISCONNECT", f"Error: {e}. Reconnecting in {backoff}s")
                logger.warning("SignalR connection error: %s. Reconnecting in %.1fs...", e, backoff)
                if not self.running:
                    break
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30.0)

        self.connection_status = "DISCONNECTED"
        self._log_connection("STOP_STREAMING", "Streaming stopped gracefully.")

    def stop(self) -> None:
        """Gracefully stop streaming."""
        self.running = False
        self.connection_status = "DISCONNECTED"
        if self.run_task and not self.run_task.done():
            self.run_task.cancel()
        self._log_connection("MANUAL_STOP", "Client stopped.")
