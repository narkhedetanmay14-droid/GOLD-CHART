# XAU/USD AI Trading Research: Part A & Part B Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete data, market structure, feature foundation (Part A), and strategy research, ML/DL modeling, ensembling, and parameter optimization (Part B) for XAU/USD AI trading on real BiQuote market data.

**Architecture:** A modular Python pipeline in `src/` driven by pure-Python modules that handle ingestion, validation, resampled candle construction, leak-free market structure analytics, vectorized technical features, triple-barrier labeling (1:2 R:R), ML/DL training, stacking ensembles, and Optuna optimization. Outputs feed directly into 10 executable, valid JSON Jupyter Notebooks (01–10).

**Tech Stack:** Python 3.14, pandas, numpy, scipy, scikit-learn, pyarrow, matplotlib, seaborn, pyyaml, requests, tqdm, nbformat, nbconvert, pytest.

**Spec:** `docs/superpowers/specs/2026-11-12-part-a-and-b-design.md`

## Global Constraints

- Absolute path for project: `C:\Users\ASUS\Desktop\gold_chart`.
- Use genuine BiQuote market data from live REST endpoints (`https://biquote.io/api/`). No synthetic data for production pipelines.
- Zero future data leakage: rolling windows must look backward only; swing highs/lows must require confirmed forward lag before signaling.
- Risk/Reward ratio strictly preserved at 1:2 (1R risk distance, 2R target distance).
- All 10 notebooks must be valid JSON `.ipynb` files containing markdown, code, and execution outputs.
- No deletion or destruction of existing user files.

## Review Focus

1. **BiQuote Rate Limits & Transient HTTP Failures:** Handles HTTP 429 and network timeouts with exponential backoff and jitter.
2. **Intrabar Ambiguity in 1:2 R:R Hits:** When both target and stop are reached in the same candle, conservative resolution assigns stop-loss hit (loss).
3. **Data Leakage in Scalers & Transformations:** StandardScalers and quantile transformers must be fit strictly on training splits and only applied to validation/test sets.
4. **Swing Detection Lag:** A swing high at index $i$ requires confirmation at $i+N$; the signal timestamp must be $i+N$, never $i$.
5. **Ensemble Out-of-Fold Leakage:** Stacking meta-models must train exclusively on out-of-fold predictions produced by purged chronological K-Fold splits.

---

### Task 1: Configuration & Central Config Loader

**Files:**
- Create: `src/config_loader.py`
- Modify: `config/settings.yaml`
- Modify: `config/biquote.yaml`
- Test: `tests/test_config_loader.py`

**Interfaces:**
- Produces: `ConfigLoader.get_settings() -> dict`, `ConfigLoader.get_biquote_config() -> dict`, `ConfigLoader.resolve_path(rel_path: str) -> Path`

- [ ] **Step 1: Write test for ConfigLoader**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/config_loader.py` and populate YAML configs**
- [ ] **Step 4: Verify test passes**

---

### Task 2: BiQuote REST Ingestion & Historical Downloader

**Files:**
- Create: `src/biquote_client.py`
- Create: `src/historical_downloader.py`
- Test: `tests/test_biquote_client.py`
- Output: `data/raw/historical_candles/`, `data/raw/historical_ticks/`, `data/metadata/data_availability.json`

**Interfaces:**
- Produces: `BiQuoteClient.get_tick(symbol: str) -> dict`, `BiQuoteClient.get_ohlc(symbol: str, interval: str, limit: int) -> pd.DataFrame`, `HistoricalDownloader.download_all() -> dict`

- [ ] **Step 1: Write unit tests for BiQuote client and downloader with mocked and live responses**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/biquote_client.py` with retries, timeout handling, and ISO 8601 parsing**
- [ ] **Step 4: Implement `src/historical_downloader.py` supporting multi-timeframe fetching (1m, 5m, 15m, 1h, 4h, 1d) and raw storage**
- [ ] **Step 5: Run tests and execute live download to populate `data/raw/`**

---

### Task 3: Data Validation, Cleansing & Candle Aggregation

**Files:**
- Create: `src/data_validator.py`
- Create: `src/data_processor.py`
- Create: `src/candle_builder.py`
- Test: `tests/test_data_processing.py`
- Output: `data/processed/clean_candles.parquet`, `data/processed/clean_ticks.parquet`, `data/quality_reports/cleaning_report.json`

**Interfaces:**
- Produces: `DataValidator.validate_candles(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]`, `DataProcessor.clean_pipeline() -> dict`, `CandleBuilder.resample(df: pd.DataFrame, timeframe: str) -> pd.DataFrame`

- [ ] **Step 1: Write tests for OHLC validation, anomaly spikes, bid/ask consistency, and resampling**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/data_validator.py` with strict checks**
- [ ] **Step 4: Implement `src/data_processor.py` for UTC normalization, deduplication, and quality logging**
- [ ] **Step 5: Implement `src/candle_builder.py` for time-weighted resampling**
- [ ] **Step 6: Run tests and execute pipeline to generate clean processed datasets**

---

### Task 4: Market Structure & Smart Money Concepts Engine

**Files:**
- Create: `src/market_structure.py`
- Test: `tests/test_market_structure.py`
- Output: `data/processed/market_structure.parquet`, `results/market_structure/`

**Interfaces:**
- Produces: `MarketStructureEngine.detect_swings(df: pd.DataFrame, window: int) -> pd.DataFrame`, `MarketStructureEngine.detect_bos_choch(df: pd.DataFrame) -> pd.DataFrame`, `MarketStructureEngine.detect_fvg(df: pd.DataFrame) -> pd.DataFrame`, `MarketStructureEngine.detect_liquidity(df: pd.DataFrame) -> pd.DataFrame`

- [ ] **Step 1: Write tests verifying swing detection delay (asserting no lookahead bias at confirmation time)**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/market_structure.py` with confirmed swing highs/lows, HH/HL/LH/LL, BOS, CHoCH, FVG, EQH/EQL, and session levels (Asia, London, NY)**
- [ ] **Step 4: Run tests and generate `market_structure.parquet`**

---

### Task 5: Technical Indicators & Unified Feature Engine

**Files:**
- Create: `src/indicators.py`
- Create: `src/feature_engine.py`
- Test: `tests/test_feature_engine.py`
- Output: `data/features/xauusd_features.parquet`, `data/metadata/feature_dictionary.json`, `data/quality_reports/feature_report.json`

**Interfaces:**
- Produces: `TechnicalIndicators.compute_all(df: pd.DataFrame) -> pd.DataFrame`, `FeatureEngine.build_feature_dataset() -> Tuple[pd.DataFrame, dict]`

- [ ] **Step 1: Write tests for indicator accuracy (EMA, RSI, MACD, ATR, ADX, Bollinger) and leakage check (future row perturbation test)**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/indicators.py` with vectorized pure numpy/pandas algorithms**
- [ ] **Step 4: Implement `src/feature_engine.py` to join indicators, price action wick/body metrics, and market structure states**
- [ ] **Step 5: Run tests and generate `data/features/xauusd_features.parquet` and `feature_dictionary.json`**

---

### Task 6: Part A Jupyter Notebooks (01 to 05)

**Files:**
- Create: `notebooks/01_data_collection.ipynb`
- Create: `notebooks/02_data_cleaning.ipynb`
- Create: `notebooks/03_exploratory_analysis.ipynb`
- Create: `notebooks/04_market_structure.ipynb`
- Create: `notebooks/05_feature_engineering.ipynb`

- [ ] **Step 1: Build valid `.ipynb` JSON notebooks containing markdown narrative, code importing `src/` modules, and visualization outputs**
- [ ] **Step 2: Execute each notebook from top to bottom using `nbconvert` / Python runner**
- [ ] **Step 3: Verify outputs in `data/`, `logs/`, `results/eda/`, `results/market_structure/`**

---

### Task 7: Part A Test Suite & Verification

**Files:**
- Create: `tests/test_part_a.py`

- [ ] **Step 1: Consolidate comprehensive tests for Part A modules into `tests/test_part_a.py`**
- [ ] **Step 2: Execute pytest across Part A tests and ensure 100% PASS**

---

### Task 8: Part B Strategy Engine & Rule-Based Research

**Files:**
- Create: `src/strategy_engine.py`
- Create: `config/strategy.yaml`
- Output: `data/strategy_results/strategy_signals.parquet`, `results/strategies/strategy_comparison.csv`

**Interfaces:**
- Produces: `StrategyEngine.generate_signals(df: pd.DataFrame) -> pd.DataFrame`, `StrategyEngine.evaluate_strategy(signals: pd.Series, df: pd.DataFrame) -> dict`

- [ ] **Step 1: Write tests for 10 systematic strategies (S01 to S10)**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/strategy_engine.py` and populate `config/strategy.yaml`**
- [ ] **Step 4: Run tests and generate strategy comparison metrics (Win Rate, Profit Factor, Expectancy, Max Drawdown)**

---

### Task 9: Part B Label Generation with 1:2 R:R Triple-Barrier

**Files:**
- Create: `src/label_generator.py`
- Test: `tests/test_label_generator.py`
- Output: `data/labels/strategy_labels.parquet`

**Interfaces:**
- Produces: `LabelGenerator.triple_barrier_labels(df: pd.DataFrame, risk_rr: float = 2.0, horizon: int = 15) -> pd.DataFrame`

- [ ] **Step 1: Write tests for 1:2 R:R barrier detection and intrabar collision handling**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/label_generator.py` with zero lookahead in features and documented barrier hits**
- [ ] **Step 4: Run tests and generate `data/labels/strategy_labels.parquet`**

---

### Task 10: Part B Validation Utilities & Model Evaluator

**Files:**
- Create: `src/validation_utils.py`
- Create: `src/model_evaluator.py`

**Interfaces:**
- Produces: `ValidationUtils.chronological_split(df: pd.DataFrame, train_ratio: float, val_ratio: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]`, `ModelEvaluator.evaluate_classification(y_true, y_pred, y_prob) -> dict`

- [ ] **Step 1: Write tests for chronological split integrity and metric calculations (Brier score, Expectancy)**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/validation_utils.py` and `src/model_evaluator.py`**
- [ ] **Step 4: Verify tests pass**

---

### Task 11: Part B Machine Learning & Deep Learning Model Trainers

**Files:**
- Create: `src/model_trainer.py`
- Create: `src/model_registry.py`
- Create: `config/model.yaml`
- Output: `models/candidates/`, `models/trained/`, `results/machine_learning/model_comparison.csv`

**Interfaces:**
- Produces: `ModelTrainer.train_ml_models(X_train, y_train, X_val, y_val) -> dict`, `ModelTrainer.train_dl_models(X_seq_train, y_seq_train) -> dict`, `ModelRegistry.save_model(model, metadata) -> str`

- [ ] **Step 1: Write tests for model training pipeline and artifact serialization**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/model_trainer.py` with Scikit-learn (RF, ET, HGB, LogReg, SVM) and PyTorch sequence models (LSTM, GRU, 1D-CNN) with CPU fallback**
- [ ] **Step 4: Implement `src/model_registry.py` for provenance tracking**
- [ ] **Step 5: Run tests and save trained models**

---

### Task 12: Part B Ensemble Engine & Disagreement Filtering

**Files:**
- Create: `src/ensemble_engine.py`
- Output: `results/ensembles/ensemble_comparison.csv`

**Interfaces:**
- Produces: `EnsembleEngine.voting_ensemble(predictions: dict, weights: dict) -> np.ndarray`, `EnsembleEngine.stacking_meta_learner(oof_predictions: np.ndarray, y_train: np.ndarray) -> object`, `EnsembleEngine.disagreement_filter(pred_ml, pred_dl) -> np.ndarray`

- [ ] **Step 1: Write tests for voting, out-of-fold stacking, and disagreement detection**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/ensemble_engine.py`**
- [ ] **Step 4: Run tests and verify performance against individual models**

---

### Task 13: Part B Hyperparameter Optimization & Robustness Engine

**Files:**
- Create: `src/optimization_engine.py`
- Create: `config/optimization.yaml`
- Output: `results/optimization/best_parameters.json`, `models/validated/`

**Interfaces:**
- Produces: `OptimizationEngine.optimize(objective_fn, search_space, n_trials) -> dict`

- [ ] **Step 1: Write tests for optimization convergence and parameter bounds**
- [ ] **Step 2: Run test to verify failure**
- [ ] **Step 3: Implement `src/optimization_engine.py` with multi-objective fitness score**
- [ ] **Step 4: Run tests and verify optimization history**

---

### Task 14: Part B Jupyter Notebooks (06 to 10)

**Files:**
- Create: `notebooks/06_strategy_research.ipynb`
- Create: `notebooks/07_machine_learning.ipynb`
- Create: `notebooks/08_deep_learning.ipynb`
- Create: `notebooks/09_ensemble_learning.ipynb`
- Create: `notebooks/10_strategy_optimization.ipynb`

- [ ] **Step 1: Build valid `.ipynb` JSON notebooks importing Part B modules**
- [ ] **Step 2: Execute each notebook top to bottom and capture cell outputs**
- [ ] **Step 3: Verify results saved in `results/strategies/`, `results/machine_learning/`, `results/deep_learning/`, `results/ensembles/`, `results/optimization/`**

---

### Task 15: Part B Test Suite & Verification

**Files:**
- Create: `tests/test_part_b.py`

- [ ] **Step 1: Consolidate comprehensive tests for Part B modules into `tests/test_part_b.py`**
- [ ] **Step 2: Run pytest across Part B tests and ensure 100% PASS**

---

### Task 16: Project Documentation & Environment Finalization

**Files:**
- Modify: `requirements.txt`
- Modify: `README.md`

- [ ] **Step 1: Pin all verified dependencies in `requirements.txt`**
- [ ] **Step 2: Update `README.md` with detailed execution instructions and architecture summary**
- [ ] **Step 3: Final end-to-end check**
