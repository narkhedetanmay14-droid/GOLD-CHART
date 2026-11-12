import time
import logging
from typing import Dict, Any, List, Optional
import requests
import pandas as pd

logger = logging.getLogger(__name__)

class BiQuoteClient:
    """Official BiQuote REST API client for XAU/USD market data."""

    BASE_URL = "https://biquote.io/api"

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30, retry_count: int = 3, retry_delay: float = 1.0):
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GoldChart-Research/1.0",
            "Accept": "application/json"
        })

    def _request_with_retry(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        last_error = None
        for attempt in range(self.retry_count):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 429:
                    # Rate limit exceeded - back off
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning("BiQuote rate limit hit (429). Retrying in %.1fs...", wait_time)
                    time.sleep(wait_time)
                else:
                    logger.warning("BiQuote HTTP %d: %s", resp.status_code, resp.text[:200])
                    resp.raise_for_status()
            except (requests.RequestException, ValueError) as e:
                last_error = e
                wait_time = self.retry_delay * (2 ** attempt)
                logger.warning("Request attempt %d failed: %s. Retrying in %.1fs...", attempt + 1, e, wait_time)
                time.sleep(wait_time)
        raise RuntimeError(f"Failed BiQuote request after {self.retry_count} attempts: {last_error}")

    def get_latest_tick(self, symbol: str = "XAUUSD") -> Dict[str, Any]:
        """Fetch real-time tick for symbol. Returns dict with bid, ask, mid, spread, timestamp."""
        symbol_clean = symbol.replace("/", "")
        data = self._request_with_retry(f"/{symbol_clean}")
        if isinstance(data, dict):
            # Normalize timestamp to UTC pandas Timestamp
            if "timestamp" in data:
                data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
            return data
        raise ValueError(f"Unexpected tick response format: {data}")

    def get_tick_history(self, symbol: str = "XAUUSD", count: int = 1000) -> pd.DataFrame:
        """Fetch historical ticks (up to 1,000 records)."""
        symbol_clean = symbol.replace("/", "")
        count = min(max(count, 1), 1000)
        data = self._request_with_retry(f"/{symbol_clean}/history", params={"count": count})
        if isinstance(data, list):
            df = pd.DataFrame(data)
            if not df.empty and "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                df = df.sort_values("timestamp").reset_index(drop=True)
            return df
        return pd.DataFrame()

    def get_ohlc(self, symbol: str = "XAUUSD", interval: str = "1h", limit: int = 1000) -> pd.DataFrame:
        """Fetch historical OHLC candles. Supported intervals: 1m, 5m, 15m, 30m, 1h, 4h, 1d.
        Max limit: 2000 bars.
        """
        symbol_clean = symbol.replace("/", "")
        limit = min(max(limit, 1), 2000)
        data = self._request_with_retry(f"/{symbol_clean}/ohlc", params={"interval": interval, "limit": limit})
        if isinstance(data, dict) and "bars" in data:
            bars = data["bars"]
            df = pd.DataFrame(bars)
            if not df.empty:
                # Normalize time columns
                if "openTime" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["openTime"], utc=True)
                elif "timestamp" in df.columns:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                # Drop currently unclosed bar if open
                if "isOpen" in df.columns:
                    df = df[~df["isOpen"]].copy()
                # Ensure standard numeric columns
                for col in ["open", "high", "low", "close", "volume", "tickVolume"]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                df = df.sort_values("timestamp").reset_index(drop=True)
                return df
        return pd.DataFrame()

    def get_symbol_metadata(self, symbol: str = "XAUUSD") -> Dict[str, Any]:
        """Fetch contract specs and symbol metadata."""
        symbol_clean = symbol.replace("/", "")
        return self._request_with_retry(f"/symbols/{symbol_clean}")
