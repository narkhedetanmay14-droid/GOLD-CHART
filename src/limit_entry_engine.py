import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional

class LimitEntryEngine:
    """Predicts optimal limit entry prices, 180-second touch probabilities, and time-to-touch.

    Distinguishes strictly between:
    - Touch: Market price level reaches or penetrates the limit price.
    - Fill: Order execution requires passive liquidity consumption (bid/ask crossing or trading through).
    """

    @staticmethod
    def calculate_limit_price(
        current_price: float,
        atr: float,
        direction: str = "BUY",
        pullback_pct: float = 0.5,
        bid: Optional[float] = None,
        ask: Optional[float] = None,
        market_structure: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calculate BUY LIMIT (below market) or SELL LIMIT (above market).

        Incorporates:
        - Volatility buffer: offset = atr * pullback_pct
        - Real bid/ask spread awareness
        - Market structure key swing levels if available
        """
        offset = atr * pullback_pct
        base_price = current_price

        if direction == "BUY":
            # BUY Limit rests below market bid
            if bid is not None and bid > 0:
                base_price = bid
            limit = base_price - offset

            # If bullish market structure swing low exists above deep pullback, align entry near swing low
            if market_structure and "swing_low" in market_structure:
                sw_low = float(market_structure["swing_low"])
                if limit < sw_low < base_price:
                    limit = sw_low + 0.10  # Just above support
            return round(limit, 2)

        elif direction == "SELL":
            # SELL Limit rests above market ask
            if ask is not None and ask > 0:
                base_price = ask
            limit = base_price + offset

            # If bearish market structure swing high exists below deep pullback, align entry near swing high
            if market_structure and "swing_high" in market_structure:
                sw_high = float(market_structure["swing_high"])
                if base_price < sw_high < limit:
                    limit = sw_high - 0.10  # Just below resistance
            return round(limit, 2)

        return round(current_price, 2)

    @staticmethod
    def evaluate_touch(
        future_highs: np.ndarray,
        future_lows: np.ndarray,
        limit_price: float,
        direction: str = "BUY",
        horizon_seconds: int = 180
    ) -> Tuple[bool, int]:
        """Check if limit price is touched within horizon.
        Returns (touched: bool, seconds_to_touch: int).
        """
        for sec, (h, l) in enumerate(zip(future_highs, future_lows)):
            if sec > horizon_seconds:
                break
            if direction == "BUY" and l <= limit_price <= h:
                return True, sec
            elif direction == "SELL" and l <= limit_price <= h:
                return True, sec
        return False, horizon_seconds

    @staticmethod
    def evaluate_fill(
        future_highs: np.ndarray,
        future_lows: np.ndarray,
        limit_price: float,
        direction: str = "BUY",
        spread: float = 0.20,
        horizon_seconds: int = 180
    ) -> Tuple[bool, int]:
        """Check if limit price is filled within horizon.
        Requires price to trade through limit price by at least half the spread for passive fill.
        """
        half_spread = spread / 2.0
        for sec, (h, l) in enumerate(zip(future_highs, future_lows)):
            if sec > horizon_seconds:
                break
            if direction == "BUY" and l <= (limit_price - half_spread):
                return True, sec
            elif direction == "SELL" and h >= (limit_price + half_spread):
                return True, sec
        return False, horizon_seconds
