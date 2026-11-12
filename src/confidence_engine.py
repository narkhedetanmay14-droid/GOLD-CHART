import numpy as np
from typing import Dict, Any

class ConfidenceEngine:
    """Computes calibrated trade confidence score (0 to 100)."""

    def __init__(self, calibrator=None):
        self.calibrator = calibrator

    def predict_confidence(self, raw_probability: float) -> float:
        if self.calibrator is not None:
            try:
                prob = self.calibrator.predict_proba(np.array([raw_probability]))[0]
            except Exception:
                prob = raw_probability
        else:
            prob = raw_probability
        return float(np.clip(prob * 100.0, 0.0, 100.0))

    @staticmethod
    def evaluate_gate(confidence: float, threshold: float = 90.0) -> bool:
        return confidence >= threshold
