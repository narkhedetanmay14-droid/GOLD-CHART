import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, log_loss, brier_score_loss
from typing import Dict, Any

class ModelEvaluator:
    """Evaluates classification models and trading performance metrics."""

    @staticmethod
    def evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, Any]:
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        }
        if y_prob is not None:
            try:
                metrics["log_loss"] = float(log_loss(y_true, y_prob))
            except Exception:
                pass
        return metrics
