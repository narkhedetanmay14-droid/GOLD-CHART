import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import joblib

logger = logging.getLogger(__name__)

class ModelRegistry:
    """Manages versioned model artifacts and their training provenance metadata."""

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.candidates_dir = self.models_dir / "candidates"
        self.trained_dir = self.models_dir / "trained"
        self.validated_dir = self.models_dir / "validated"
        self.rejected_dir = self.models_dir / "rejected"

        for d in [self.candidates_dir, self.trained_dir, self.validated_dir, self.rejected_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def save_model(
        self,
        model: Any,
        model_name: str,
        stage: str = "trained",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        target_dir = getattr(self, f"{stage}_dir", self.trained_dir)
        model_path = target_dir / f"{model_name}.joblib"
        meta_path = target_dir / f"{model_name}_metadata.json"

        # Save model
        joblib.dump(model, model_path)

        # Save metadata
        meta = metadata or {}
        meta["model_name"] = model_name
        meta["stage"] = stage
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, default=str)

        logger.info("Saved model %s to %s", model_name, model_path)
        return model_path

    def load_model(self, model_name: str, stage: str = "validated") -> Any:
        target_dir = getattr(self, f"{stage}_dir", self.validated_dir)
        model_path = target_dir / f"{model_name}.joblib"
        if not model_path.exists():
            # Try trained dir
            model_path = self.trained_dir / f"{model_name}.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Model {model_name} not found in {stage} or trained directories.")
        return joblib.load(model_path)
