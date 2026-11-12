import os
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error, brier_score_loss

sys.path.insert(0, os.path.abspath("src"))

from label_generator import LabelGenerator
from validation_utils import ValidationUtils
from calibration_engine import CalibrationEngine
from model_registry import ModelRegistry

def main():
    print("=== Training Validated Real-Time Prediction Models & Calibrators ===")
    features_path = Path("data/features/xauusd_features.parquet")
    if not features_path.exists():
        print(f"Error: {features_path} does not exist.")
        sys.exit(1)

    df = pd.read_parquet(features_path)
    print(f"Loaded feature dataset: {df.shape}")

    # 1. Generate triple barrier labels (1:2 R:R, horizon 15)
    df_labeled = LabelGenerator.triple_barrier_labels(df, risk_rr=2.0, horizon=15)

    # Calculate forward realized 15-min efficiency target
    r_dist = df_labeled["atr_14"].values * 1.5
    target_dist = 2.0 * r_dist
    target_dist = np.where(target_dist <= 0, 1.0, target_dist)
    realized_efficiency = np.clip((df_labeled["mfe"].values / target_dist) * 100.0, 0.0, 100.0)
    df_labeled["target_efficiency"] = realized_efficiency

    # Calculate forward limit touch target (e.g. 0.3 ATR pullback touched within next 180s / 3 bars)
    highs = df_labeled["high"].values
    lows = df_labeled["low"].values
    closes = df_labeled["close"].values
    n = len(df_labeled)
    touch_labels = np.zeros(n, dtype=int)
    time_to_touch = np.full(n, 180.0, dtype=float)

    for i in range(n - 3):
        entry_pullback = closes[i] - (r_dist[i] * 0.3)
        # Check if lowest low in next 3 bars touched pullback
        fwd_min = lows[i+1 : i+4].min()
        if fwd_min <= entry_pullback:
            touch_labels[i] = 1
            # Approximate time to touch (1m to 3m)
            touch_idx = np.where(lows[i+1 : i+4] <= entry_pullback)[0][0]
            time_to_touch[i] = float((touch_idx + 1) * 60)

    df_labeled["target_touch"] = touch_labels
    df_labeled["target_time_to_touch"] = time_to_touch

    # 2. Chronological split (60% train, 20% validation, 20% test)
    train_df, val_df, test_df = ValidationUtils.chronological_split(df_labeled, 0.6, 0.2)

    # Exclude non-stationary absolute price levels to ensure models generalize across price regimes
    non_stationary = [
        'open', 'high', 'low', 'close', 'openTime', 'timestamp', 'isOpen',
        'ema_9', 'ema_21', 'ema_50', 'ema_200', 'sma_20', 'sma_50',
        'bb_upper', 'bb_lower', 'target_label', 'mfe', 'mae',
        'target_efficiency', 'target_touch', 'target_time_to_touch'
    ]
    feature_cols = [c for c in df.columns if c not in non_stationary]

    print(f"Stationary Features count: {len(feature_cols)}")
    print(f"Features: {feature_cols}")
    print(f"Split sizes - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    X_train, y_train = train_df[feature_cols], train_df['target_label']
    X_val, y_val = val_df[feature_cols], val_df['target_label']
    X_test, y_test = test_df[feature_cols], test_df['target_label']

    registry = ModelRegistry(models_dir="models")

    # -------------------------------------------------------------
    # Model 1: Direction Classifier (Random Forest)
    # -------------------------------------------------------------
    print("Training Direction Classifier (Random Forest)...")
    dir_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    dir_model.fit(X_train, y_train)

    val_preds = dir_model.predict(X_val)
    val_probs = dir_model.predict_proba(X_val)
    test_preds = dir_model.predict(X_test)
    test_probs = dir_model.predict_proba(X_test)

    dir_meta = {
        "model_type": "direction_random_forest",
        "features": feature_cols,
        "classes": dir_model.classes_.tolist(),
        "train_rows": len(X_train),
        "val_accuracy": float(accuracy_score(y_val, val_preds)),
        "test_accuracy": float(accuracy_score(y_test, test_preds))
    }
    registry.save_model(dir_model, "direction_classifier", stage="validated", metadata=dir_meta)
    registry.save_model(dir_model, "direction_classifier", stage="trained", metadata=dir_meta)

    # -------------------------------------------------------------
    # Model 2: Confidence Calibrator (Platt Scaling via CalibrationEngine)
    # -------------------------------------------------------------
    print("Fitting Trade Confidence Calibrator on Validation Set...")
    # Calibrate probability of winning trade (TP hit before SL, target_label in [1, -1])
    # Target: binary win (1 if target_label != 0 else 0)
    y_val_binary = (y_val.values != 0).astype(int)
    y_test_binary = (y_test.values != 0).astype(int)

    # Max raw predicted probability from direction model
    val_raw_conf = np.max(val_probs, axis=1)
    test_raw_conf = np.max(test_probs, axis=1)

    calibrator = CalibrationEngine(method="sigmoid")
    calibrator.fit(val_raw_conf, y_val_binary)

    cal_val_probs = calibrator.predict_proba(val_raw_conf)
    cal_test_probs = calibrator.predict_proba(test_raw_conf)

    ece_val = CalibrationEngine.expected_calibration_error(y_val_binary, cal_val_probs)
    ece_test = CalibrationEngine.expected_calibration_error(y_test_binary, cal_test_probs)
    brier_test = float(brier_score_loss(y_test_binary, cal_test_probs))

    calib_meta = {
        "model_type": "confidence_calibrator_sigmoid",
        "method": "sigmoid_platt_scaling",
        "features": ["raw_model_confidence"],
        "train_rows": len(val_raw_conf),
        "val_ece": float(ece_val),
        "test_ece": float(ece_test),
        "test_brier_score": float(brier_test),
        "calibration_evidence": "Calibrated against actual target-before-stop outcomes"
    }
    registry.save_model(calibrator, "confidence_calibrator", stage="validated", metadata=calib_meta)
    registry.save_model(calibrator, "confidence_calibrator", stage="trained", metadata=calib_meta)

    # -------------------------------------------------------------
    # Model 3: 15-Minute Efficiency Forecaster
    # -------------------------------------------------------------
    print("Training 15-Minute Efficiency Forecasting Regressor...")
    eff_model = HistGradientBoostingRegressor(max_depth=3, min_samples_leaf=15, l2_regularization=1.0, random_state=42)
    eff_model.fit(X_train, train_df["target_efficiency"])

    val_eff_preds = eff_model.predict(X_val)
    test_eff_preds = eff_model.predict(X_test)

    eff_mae = float(mean_absolute_error(test_df["target_efficiency"], test_eff_preds))
    eff_rmse = float(np.sqrt(mean_squared_error(test_df["target_efficiency"], test_eff_preds)))

    eff_meta = {
        "model_type": "efficiency_forecaster_hist_gb",
        "target": "15_min_favourable_excursion_efficiency",
        "training_timestamp_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "training_dataset": "data/features/xauusd_features.parquet",
        "forecast_horizon": "15_minutes",
        "features": feature_cols,
        "train_rows": len(X_train),
        "val_mae": float(mean_absolute_error(val_df["target_efficiency"], val_eff_preds)),
        "test_mae": eff_mae,
        "test_rmse": eff_rmse
    }
    registry.save_model(eff_model, "efficiency_forecaster", stage="validated", metadata=eff_meta)
    registry.save_model(eff_model, "efficiency_forecaster", stage="trained", metadata=eff_meta)

    # -------------------------------------------------------------
    # Model 4: Limit-Entry Touch Probability & Time-to-Touch Models
    # -------------------------------------------------------------
    print("Training Limit-Entry Touch & Time Models...")
    touch_model = HistGradientBoostingClassifier(max_depth=3, min_samples_leaf=15, l2_regularization=1.0, random_state=42)
    touch_model.fit(X_train, train_df["target_touch"])

    time_model = HistGradientBoostingRegressor(max_depth=3, min_samples_leaf=15, l2_regularization=1.0, random_state=42)
    time_model.fit(X_train, train_df["target_time_to_touch"])

    touch_meta = {
        "model_type": "limit_touch_classifier",
        "features": feature_cols,
        "train_rows": len(X_train),
        "test_accuracy": float(accuracy_score(test_df["target_touch"], touch_model.predict(X_test)))
    }
    registry.save_model(touch_model, "limit_touch_model", stage="validated", metadata=touch_meta)
    registry.save_model(touch_model, "limit_touch_model", stage="trained", metadata=touch_meta)

    time_meta = {
        "model_type": "limit_time_regressor",
        "features": feature_cols,
        "train_rows": len(X_train),
        "test_mae": float(mean_absolute_error(test_df["target_time_to_touch"], time_model.predict(X_test)))
    }
    registry.save_model(time_model, "limit_time_model", stage="validated", metadata=time_meta)
    registry.save_model(time_model, "limit_time_model", stage="trained", metadata=time_meta)

    print("Successfully trained, validated, and registered all prediction pipeline models!")

if __name__ == "__main__":
    main()
