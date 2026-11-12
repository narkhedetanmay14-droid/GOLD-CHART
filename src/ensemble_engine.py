import numpy as np
from typing import Dict, Any, List
from sklearn.linear_model import LogisticRegression

class EnsembleEngine:
    """Combines model predictions through voting, stacking, and disagreement detection."""

    @staticmethod
    def soft_voting(probabilities: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray:
        if not probabilities:
            return np.array([])
        if weights is None:
            weights = [1.0 / len(probabilities)] * len(probabilities)
        weighted_sum = sum(w * p for w, p in zip(weights, probabilities))
        return weighted_sum

    @staticmethod
    def hard_voting(predictions: List[np.ndarray]) -> np.ndarray:
        if not predictions:
            return np.array([])
        stacked = np.vstack(predictions)
        # Mode along columns
        from scipy.stats import mode
        m, _ = mode(stacked, axis=0)
        return m.flatten()

    @staticmethod
    def detect_disagreement(pred_a: np.ndarray, pred_b: np.ndarray) -> np.ndarray:
        """Filter out signals where two key models disagree (e.g. BUY vs SELL -> NO_TRADE)."""
        disagreed = (pred_a != pred_b)
        return disagreed
