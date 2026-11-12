import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class ExecutionSimulator:
    """Simulates realistic trade executions with spread, slippage, latency, touch vs fill, and intrabar ambiguity handling."""

    def __init__(
        self,
        spread: float = 0.20,
        slippage: float = 0.05,
        commission: float = 0.02,
        fill_probability: float = 0.95
    ):
        self.spread = spread
        self.slippage = slippage
        self.commission = commission
        self.fill_probability = fill_probability

    def simulate_entry(self, price: float, direction: str, is_limit: bool = False) -> Dict[str, Any]:
        """Simulate an entry fill.
        BUY enters at ask (price + spread/2) + slippage.
        SELL enters at bid (price - spread/2) - slippage.
        """
        if direction == "BUY":
            fill_price = price + (self.spread / 2.0) + self.slippage
        elif direction == "SELL":
            fill_price = price - (self.spread / 2.0) - self.slippage
        else:
            return {"filled": False, "price": None, "cost": 0.0}

        return {
            "filled": True,
            "fill_price": fill_price,
            "slippage": self.slippage,
            "spread": self.spread,
            "commission": self.commission,
            "total_cost": self.spread + self.slippage + self.commission
        }

    def simulate_exit(self, price: float, direction: str) -> float:
        """Simulate exit fill.
        BUY exits at bid (price - spread/2) - slippage.
        SELL exits at ask (price + spread/2) + slippage.
        """
        if direction == "BUY":
            return price - (self.spread / 2.0) - self.slippage - self.commission
        else:
            return price + (self.spread / 2.0) + self.slippage + self.commission

    def resolve_intrabar(self, high: float, low: float, stop: float, target: float, direction: str) -> str:
        """Handle intrabar ambiguity when both stop and target are within [low, high].
        Conservative institutional convention: assume stop-loss was touched first.
        """
        if direction == "BUY":
            hit_target = high >= target
            hit_stop = low <= stop
            if hit_target and hit_stop:
                return "AMBIGUOUS_LOSS"  # Conservative rule
            elif hit_target:
                return "WIN"
            elif hit_stop:
                return "LOSS"
        elif direction == "SELL":
            hit_target = low <= target
            hit_stop = high >= stop
            if hit_target and hit_stop:
                return "AMBIGUOUS_LOSS"
            elif hit_target:
                return "WIN"
            elif hit_stop:
                return "LOSS"
        return "PENDING"
