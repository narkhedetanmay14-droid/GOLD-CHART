import sys, os
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath("src"))

from label_generator import LabelGenerator
from validation_utils import ValidationUtils
from model_trainer import ModelTrainer
from model_evaluator import ModelEvaluator
from model_registry import ModelRegistry

print("Starting baseline model training pipeline...")

features_path = Path("data/features/xauusd_features.parquet")
if not features_path.exists():
    print(f"Error: {features_path} does not exist.")
    sys.exit(1)

df = pd.read_parquet(features_path)
df_labeled = LabelGenerator.triple_barrier_labels(df, risk_rr=2.0, horizon=15)

train_df, val_df, test_df = ValidationUtils.chronological_split(df_labeled, 0.6, 0.2)
feature_cols = [c for c in df.select_dtypes(include=['float64', 'int64', 'bool']).columns if c not in ['target_label', 'mfe', 'mae']]

X_train, y_train = train_df[feature_cols], train_df['target_label']
X_val, y_val = val_df[feature_cols], val_df['target_label']
X_test, y_test = test_df[feature_cols], test_df['target_label']

trainer = ModelTrainer(random_state=42)
registry = ModelRegistry(models_dir="models")

for model_name in ["hist_gradient_boosting", "random_forest", "extra_trees", "logistic_regression"]:
    print(f"Training {model_name}...")
    model = trainer.train_model(model_name, X_train, y_train)
    val_preds = model.predict(X_val)
    test_preds = model.predict(X_test)

    val_metrics = ModelEvaluator.evaluate_classification(y_val, val_preds)
    test_metrics = ModelEvaluator.evaluate_classification(y_test, test_preds)

    metadata = {
        "model_type": model_name,
        "features": feature_cols,
        "train_rows": len(X_train),
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "train_period": {
            "start": str(train_df['timestamp'].min()) if 'timestamp' in train_df.columns else "N/A",
            "end": str(train_df['timestamp'].max()) if 'timestamp' in train_df.columns else "N/A"
        }
    }

    # Save to candidates and trained
    registry.save_model(model, model_name, stage="trained", metadata=metadata)
    print(f"Model {model_name} trained and registered. Test Accuracy: {test_metrics['accuracy']:.4f}")

print("All baseline models successfully trained and registered!")
