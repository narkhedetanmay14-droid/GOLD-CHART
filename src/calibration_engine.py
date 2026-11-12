import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from typing import Dict, Any, Tuple

class CalibrationEngine:
    """Calibrates model raw probabilities against empirical target-before-stop win rates."""

    def __init__(self, method: str = "sigmoid"):
        self.method = method
        self.calibrator = None

    def fit(self, raw_probs: np.ndarray, y_true: np.ndarray):
        raw_probs = np.clip(raw_probs, 1e-6, 1 - 1e-6)
        if self.method == "sigmoid":
            # Platt scaling (Logistic Regression on log-odds)
            log_odds = np.log(raw_probs / (1.0 - raw_probs)).reshape(-1, 1)
            self.calibrator = LogisticRegression(C=1.0, solver="lbfgs")
            self.calibrator.fit(log_odds, y_true)
        else:
            self.calibrator = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            self.calibrator.fit(raw_probs, y_true)

    def predict_proba(self, raw_probs: np.ndarray) -> np.ndarray:
        raw_probs = np.clip(raw_probs, 1e-6, 1 - 1e-6)
        if self.calibrator is None:
            return raw_probs
        if self.method == "sigmoid":
            log_odds = np.log(raw_probs / (1.0 - raw_probs)).reshape(-1, 1)
            return self.calibrator.predict_proba(log_odds)[:, 1]
        else:
            return self.calibrator.predict(raw_probs)

    @staticmethod
    def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
        bin_edges = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        n = len(y_true)
        for i in range(n_bins):
            bin_mask = (y_prob >= bin_edges[i]) & (y_prob < bin_edges[i+1])
            bin_size = np.sum(bin_mask)
            if bin_size > 0:
                bin_acc = np.mean(y_true[bin_mask])
                bin_conf = np.mean(y_prob[bin_mask])
                ece += (bin_size / n) * np.abs(bin_acc - bin_conf)
        return float(ece)

    @staticmethod
    def evaluate(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
        return {
            "brier_score": float(brier_score_loss(y_true, y_prob)),
            "ece": CalibrationEngine.expected_calibration_error(y_true, y_prob)
        }
