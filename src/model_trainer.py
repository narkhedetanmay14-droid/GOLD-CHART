import logging
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Trains and evaluates machine learning classification models."""

    SUPPORTED_MODELS = {
        "hist_gradient_boosting": HistGradientBoostingClassifier,
        "random_forest": RandomForestClassifier,
        "extra_trees": ExtraTreesClassifier,
        "logistic_regression": LogisticRegression
    }

    def __init__(self, random_state: int = 42):
        self.random_state = random_state

    def train_model(
        self,
        model_name: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        params: Optional[Dict[str, Any]] = None
    ) -> Any:
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(f"Model '{model_name}' not supported. Choose from {list(self.SUPPORTED_MODELS.keys())}")

        model_cls = self.SUPPORTED_MODELS[model_name]
        init_params = {"random_state": self.random_state}
        if model_name == "logistic_regression":
            init_params["max_iter"] = 1000
        if params:
            init_params.update(params)

        model = model_cls(**init_params)
        model.fit(X_train, y_train)
        return model

    def train_all_baselines(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ) -> Dict[str, Any]:
        trained_models = {}
        for name in self.SUPPORTED_MODELS.keys():
            try:
                trained_models[name] = self.train_model(name, X_train, y_train)
            except Exception as e:
                logger.warning("Failed to train model %s: %s", name, e)
        return trained_models
