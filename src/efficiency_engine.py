import numpy as np
import pandas as pd
from typing import Dict, Any

class EfficiencyEngine:
    """Predicts 15-minute favourable excursion efficiency relative to target distance (0 to 100)."""

    @staticmethod
    def calculate_realized_efficiency(
        highs: np.ndarray,
        lows: np.ndarray,
        entry: float,
        target: float,
        direction: str = "BUY"
    ) -> float:
        target_distance = abs(target - entry)
        if target_distance == 0:
            return 0.0

        if direction == "BUY":
            mfe = max(0.0, highs.max() - entry)
        else:
            mfe = max(0.0, entry - lows.min())

        efficiency = min(100.0, (mfe / target_distance) * 100.0)
        return float(efficiency)

    @staticmethod
    def evaluate_gate(efficiency_score: float, threshold: float = 90.0) -> bool:
        return efficiency_score >= threshold
