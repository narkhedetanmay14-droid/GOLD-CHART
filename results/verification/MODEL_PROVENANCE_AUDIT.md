# Model Provenance Audit Report

- **Training Pipeline:** Chronological train/validation/test splits with zero future leakage.
- **Models:** HistGradientBoosting, Random Forest, Logistic Regression, Isotonic/Platt Calibrators.
- **Registry:** Artifacts saved to `models/candidates/`, `models/trained/`, and `models/validated/` with metadata tracking.
