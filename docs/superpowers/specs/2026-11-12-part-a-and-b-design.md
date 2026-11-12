# XAU/USD AI Trading Research: Part A & Part B Architectural Design

**Document ID:** SPEC-2026-11-12-XAUUSD-PART-A-B  
**Date:** 2026-11-12  
**Target Directory:** `C:\Users\ASUS\Desktop\gold_chart`  
**Status:** Approved  

---

## 1. Executive Summary & Goals

The objective of this project is to build an institutional-grade, end-to-end quantitative AI research and real-time prediction system for **XAU/USD (Gold vs. US Dollar)**. 

This specification covers:
- **Part A: Data Foundation & Market Understanding** (Notebooks 01–05, data ingestion from BiQuote REST API, cleaning, resampled candle construction, market structure analytics, technical and price-action feature engineering).
- **Part B: Strategy Research & Model Development** (Notebooks 06–10, systematic strategy combinations, leakage-safe target labeling, machine learning & sequence models, ensemble stacking/voting, Bayesian/Optuna parameter optimization, model versioning and registry).

All source code must be clean, testable, fully implemented in Python, and executed within valid Jupyter notebooks (`.ipynb` JSON format) that run top-to-bottom.

---

## 2. Directory Structure & File Map

```text
gold_chart/
├── config/
│   ├── settings.yaml              # General project configuration (paths, symbol, timezone)
│   ├── biquote.yaml               # BiQuote REST & streaming endpoints, rate limits, timeouts
│   ├── strategy.yaml              # Strategy parameters and experiment definitions
│   ├── model.yaml                 # ML/DL architectures, hyperparameters, sequence lengths
│   └── optimization.yaml          # Search spaces, objective weights, budgets
│
├── data/
│   ├── raw/
│   │   ├── historical_ticks/      # Unmodified raw tick data from BiQuote
│   │   └── historical_candles/    # Unmodified raw OHLC bars (1m, 5m, 15m, 1h, 4h, 1d)
│   ├── processed/
│   │   ├── clean_ticks.parquet    # UTC-normalized, validated, duplicate-free ticks
│   │   ├── clean_candles.parquet  # Validated OHLC candles with spread & volume
│   │   └── market_structure.parquet # Swing highs/lows, BOS, CHoCH, FVG, liquidity pools
│   ├── features/
│   │   └── xauusd_features.parquet # Combined indicator, price action, and structure features
│   ├── labels/
│   │   └── strategy_labels.parquet # 1:2 R:R triple-barrier target labels without lookahead
│   ├── strategy_results/
│   │   └── strategy_signals.parquet# Raw and filtered strategy signal matrices
│   ├── metadata/
│   │   ├── data_availability.json # Coverage, timestamps, missing periods
│   │   └── feature_dictionary.json# Complete definition, formula, input, and safety of each feature
│   └── quality_reports/
│       ├── cleaning_report.json   # Anomaly log, duplicate counts, price validation results
│       ├── eda_report.json        # Descriptive statistics, session breakdown, volatility metrics
│       └── feature_report.json    # Correlation matrix, null statistics, distribution diagnostics
│
├── models/
│   ├── candidates/                # Newly trained model artifacts (.pkl, .pt, .json)
│   ├── trained/                   # Production-ready trained models
│   ├── validated/                 # Models passing all out-of-sample and stability gates
│   └── rejected/                  # Models failing overfit or expectancy thresholds
│
├── notebooks/
│   ├── 01_data_collection.ipynb   # Raw ingestion from BiQuote, coverage reporting
│   ├── 02_data_cleaning.ipynb     # Timestamp normalization, OHLC integrity, anomaly checks
│   ├── 03_exploratory_analysis.ipynb # Distributions, volatility, session analysis, timeframes
│   ├── 04_market_structure.ipynb  # Swings, HH/HL/LH/LL, BOS, CHoCH, FVG, Liquidity Sweeps
│   ├── 05_feature_engineering.ipynb # Vectorized indicators, PA features, multi-timeframe features
│   ├── 06_strategy_research.ipynb # 10+ systematic strategy combinations, session/regime metrics
│   ├── 07_machine_learning.ipynb  # Classification (RF, ET, GBDT, XGB, LGBM, CatB, LogReg, SVM)
│   ├── 08_deep_learning.ipynb     # Sequence models (LSTM, GRU, 1D CNN, TCN), CPU/GPU adaptive
│   ├── 09_ensemble_learning.ipynb # Hard/soft voting, stacking with OOF predictions, regime weights
│   └── 10_strategy_optimization.ipynb # Optuna TPE, parameter sensitivity, walk-forward holdout
│
├── results/
│   ├── eda/                       # Generated charts for exploratory analysis
│   ├── market_structure/          # Structure visualization charts
│   ├── strategies/                # Strategy comparison CSVs, expectancy curves
│   ├── machine_learning/          # ROC/PR curves, confusion matrices, calibration plots
│   ├── deep_learning/             # Sequence training loss curves, latency benchmarks
│   ├── ensembles/                 # Out-of-fold stacking performance reports
│   └── optimization/              # Parameter sensitivity charts, Pareto frontiers
│
├── src/
│   ├── __init__.py
│   ├── config_loader.py           # Typed configuration parsing
│   ├── biquote_client.py          # BiQuote REST client with retries and rate limiting
│   ├── historical_downloader.py   # Multi-timeframe downloader and resume manager
│   ├── data_validator.py          # Strict OHLC, tick, and timestamp validator
│   ├── data_processor.py          # Data cleansing and normalization pipeline
│   ├── candle_builder.py          # High-precision candle aggregator / resampler
│   ├── market_structure.py        # Leakage-safe swing, structure, and liquidity algorithms
│   ├── indicators.py              # Vectorized technical indicators (EMA, RSI, MACD, ATR, ADX...)
│   ├── feature_engine.py          # Unified feature generator and dictionary exporter
│   ├── strategy_engine.py         # 10+ rule-based strategy signal generators
│   ├── label_generator.py         # Triple-barrier 1:2 R:R label generator with purging
│   ├── model_trainer.py           # Sklearn / GBDT / PyTorch model training pipelines
│   ├── model_evaluator.py         # Financial metrics (Sharpe, Profit Factor, Expectancy, Brier)
│   ├── model_registry.py          # Versioned model artifact manager with provenance tracking
│   ├── ensemble_engine.py         # Voting, Stacking, Out-of-Fold meta-modeling
│   ├── optimization_engine.py     # Optuna and Grid search hyperparameter optimizers
│   └── validation_utils.py        # Purged time-series splits, leakage auditing
│
├── tests/
│   ├── test_part_a.py             # Unit & integration tests for data, structure & features
│   └── test_part_b.py             # Unit & integration tests for labels, models & ensembles
│
├── README.md                      # Complete execution and architecture guide
└── requirements.txt               # Pinned Python dependencies
```

---

## 3. Detailed Component Specifications

### 3.1 Part A: Data Foundation & Market Understanding

#### Module: `src/config_loader.py`
- Loads YAML configuration from `config/` directory.
- Resolves absolute paths relative to project root.
- Provides fallback defaults if configuration files are missing.

#### Module: `src/biquote_client.py`
- Targets official BiQuote REST API (`https://biquote.io/api/`).
- Endpoints:
  - `/api/XAUUSD`: Current tick (bid, ask, mid, spread, timestamp).
  - `/api/XAUUSD/history?count=N`: Recent tick history (up to 1,000 ticks).
  - `/api/XAUUSD/ohlc?interval={tf}&limit={limit}`: Historical OHLC bars (up to 2,000 bars per call).
  - `/api/symbols/XAUUSD`: Metadata and contract specifications.
- Implements exponential backoff with jitter (max 3 retries) and handles HTTP 429 rate limit errors.
- Parses ISO 8601 UTC timestamps into native `pandas.Timestamp`.

#### Module: `src/historical_downloader.py`
- Downloads multi-timeframe candles: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`.
- Downloads available tick history.
- Saves raw data into `data/raw/` in Parquet and JSON formats without altering source values.
- Compiles `data/metadata/data_availability.json`.

#### Module: `src/data_validator.py`
- Validates tick data: `ask >= bid`, `spread >= 0`, `mid == (bid + ask)/2`.
- Validates OHLC data:
  - `high >= max(open, close)`
  - `low <= min(open, close)`
  - `high >= low`
  - `open, high, low, close > 0`
- Price spike detection: Flags moves $> 3 \times ATR$ or statistical anomalies without silent deletion.
- Timestamp continuity: Identifies weekends, holiday breaks, and unannounced data gaps.

#### Module: `src/data_processor.py` & `src/candle_builder.py`
- Normalizes all time indices to UTC.
- Deduplicates identical timestamps, keeping verified records.
- Constructs clean candle datasets saved to `data/processed/clean_candles.parquet`.
- Logs every validation failure and filtering step into `data/quality_reports/cleaning_report.json`.

#### Module: `src/market_structure.py`
- **Zero Future Leakage Rule**: A swing high or low is confirmed ONLY after $N$ subsequent bars close without violating the peak/trough.
- Algorithms:
  - Swing Highs / Lows (configurable window $N$).
  - Trend structure: Higher High (HH), Higher Low (HL), Lower High (LH), Lower Low (LL).
  - Break of Structure (BOS): Bar close breaks previous confirmed swing in trend direction.
  - Change of Character (CHoCH): Bar close breaks previous confirmed swing opposite to current trend.
  - Fair Value Gap (FVG): Imbalance across 3 bars:
    - Bullish FVG: `Low[i] > High[i-2]`
    - Bearish FVG: `High[i] < Low[i-2]`
  - Liquidity Pools & Sweeps: Equal Highs/Lows (within tolerance $\epsilon$) where price spikes beyond the level but closes back inside.
  - Session Ranges: Asian (00:00–08:00 UTC), London (07:00–15:00 UTC), New York (12:00–20:00 UTC), Previous Day High/Low (PDH/PDL).

#### Module: `src/indicators.py` & `src/feature_engine.py`
- Vectorized technical indicators:
  - EMA: 9, 21, 50, 200
  - SMA: 20, 50
  - RSI: 14 (Wilder's smoothing)
  - MACD: Fast 12, Slow 26, Signal 9
  - ATR: 14
  - ADX: 14 (+DI, -DI)
  - Bollinger Bands: 20-period, 2 std
  - Stochastic: %K 14, %D 3
  - Rate of Change (ROC), Momentum
- Candlestick & Price Action features:
  - Body ratio, upper wick ratio, lower wick ratio, candle range relative to ATR.
  - Directional streaks (consecutive bullish/bearish bars).
  - Distance to nearest support, resistance, PDH, PDL.
- Output: `data/features/xauusd_features.parquet` and `data/metadata/feature_dictionary.json`.

---

### 3.2 Part B: Strategy Research & Model Development

#### Module: `src/strategy_engine.py`
- Encapsulates 10 systematic strategy combinations (S01–S10):
  - **S01:** Trend-Following (EMA 9/21 cross + RSI momentum).
  - **S02:** Trend-Strength (EMA 20/50 alignment + ADX > 25).
  - **S03:** Liquidity Reversal (Liquidity sweep + CHoCH confirmation).
  - **S04:** Structure Continuation (BOS confirmation + pullback to EMA 21).
  - **S05:** Imbalance Fill (FVG retracement + multi-timeframe trend alignment).
  - **S06:** Breakout & Retest (Key level breakout + ATR volatility filter).
  - **S07:** Multi-Condition Confluence (EMA trend + RSI oversold/overbought + Liquidity sweep).
  - **S08:** Session Momentum (London/NY overlap breakout + HH/HL confirmation).
  - **S09:** Mean-Reversion (Bollinger Band extreme + pin-bar rejection).
  - **S10:** High-Probability SMC Confluence (PDH/PDL sweep + FVG + CHoCH + session timing).
- Computes comprehensive trade metrics: Trade Count, Win Rate, Loss Rate, Profit Factor, Expectancy, Max Drawdown, Session breakdown.

#### Module: `src/label_generator.py`
- Implements the **Triple-Barrier Method** (de Prado):
  - Upper barrier: Profit target ($2 \times R$, where $R = \text{ATR} \times \text{multiplier}$ or swing distance).
  - Lower barrier: Stop loss ($1 \times R$, adhering strictly to the required 1:2 Risk/Reward ratio).
  - Time barrier: Horizon $H$ bars (e.g. 15 or 30 bars).
- Classes:
  - `BUY` (+1): Upper barrier touched first.
  - `SELL` (-1): Lower barrier touched first (or inverse for short setups).
  - `NO_TRADE` (0): Neither barrier touched before time expiry, or ambiguous intrabar hit.
- **Leakage Prevention**: Samples with overlapping evaluation windows are audited with purging and embargoing options.

#### Module: `src/model_trainer.py` & `src/model_evaluator.py`
- Machine Learning Models:
  - Scikit-Learn: `LogisticRegression`, `RandomForestClassifier`, `ExtraTreesClassifier`, `HistGradientBoostingClassifier`, `SVC(probability=True)`.
  - Gradient Boosted Decision Trees: `XGBClassifier`, `LGBMClassifier` (when installed, with seamless fallback to `HistGradientBoostingClassifier`).
- Deep Learning Models (Sequence forecasting via PyTorch or NumPy recurrent architectures):
  - LSTM (Long Short-Term Memory).
  - GRU (Gated Recurrent Unit).
  - 1D-CNN (Temporal Convolutional feature extractor).
- Evaluation Metrics:
  - Classification: Precision, Recall, F1-Score, ROC-AUC, PR-AUC, Confusion Matrix.
  - Calibration: Brier Score, Expected Calibration Error (ECE).
  - Financial: Expectancy per trade, Win Rate at probability threshold $\ge 0.5$, Max Drawdown.

#### Module: `src/ensemble_engine.py`
- Voting Ensembles:
  - Hard Voting (majority signal).
  - Soft Voting (probability averaging with customizable model weights).
- Stacking Meta-Learner:
  - Generates Out-of-Fold (OOF) predictions via chronological Purged Time-Series K-Fold.
  - Fits logistic meta-model strictly on OOF predictions (zero training set contamination).
- Regime-Aware Ensembles:
  - Dynamic weights adjusted based on market state (Trending vs Ranging via ADX, High vs Low Volatility via ATR).
- Disagreement Filter: Flags conflicting signals (e.g., ML predicts BUY while DL predicts SELL) as `NO_TRADE`.

#### Module: `src/optimization_engine.py`
- Parameter tuning: Grid Search, Random Search, and Bayesian Optimization (via Optuna if available, with robust pure-Python fallback).
- Multi-objective penalization:
  $$\text{Objective} = \text{Expectancy} \times \min(1.0, \frac{\text{Trade Count}}{30}) - 0.5 \times \text{Max Drawdown}$$
- Avoids over-optimizing on narrow parameter spikes.

#### Module: `src/model_registry.py` & `src/validation_utils.py`
- Model Registry: Tracks versioned artifacts in `models/candidates/`, `models/trained/`, and `models/validated/` with metadata (features, train period, OOS metrics, training timestamp).
- Validation Utils: Enforces strict chronological split: Train (60%), Validation (20%), Out-of-Sample Holdout (20%).
- Data Leakage Checker: Audits whether future rows influence current features.

---

## 4. Verification & Testing Strategy

1. **`tests/test_part_a.py`**:
   - BiQuote client mock and parsing tests.
   - OHLC anomaly and spike detection tests.
   - Resampled candle integrity (1m to 5m, 15m, 1h).
   - Market structure swing confirmation delay (proving zero future lookahead).
   - Technical indicator mathematical correctness against reference values.

2. **`tests/test_part_b.py`**:
   - Triple-barrier label generation and 1:2 R:R integrity.
   - Chronological split verification (test timestamps strictly > validation > train).
   - Model training, serialisation, and deserialisation.
   - Out-of-fold stacking leakage prevention.
   - Disagreement logic producing `NO_TRADE`.

---

## 5. Execution Sequence

1. Write Part A shared modules in `src/`.
2. Execute real historical data ingestion from BiQuote API and generate `data/raw/`.
3. Process, clean, and validate market data into `data/processed/clean_candles.parquet`.
4. Run market structure analytics and produce `data/processed/market_structure.parquet`.
5. Run feature engine and produce `data/features/xauusd_features.parquet` and `feature_dictionary.json`.
6. Write and run all 5 Part A Jupyter Notebooks (01–05).
7. Execute Part A test suite (`pytest tests/test_part_a.py`).
8. Write Part B shared modules in `src/`.
9. Generate 1:2 R:R triple-barrier target labels.
10. Train and evaluate systematic strategies (Notebook 06), ML models (Notebook 07), DL models (Notebook 08), Ensembles (Notebook 09), and Parameter Optimization (Notebook 10).
11. Write and run all 5 Part B Jupyter Notebooks (06–10).
12. Execute Part B test suite (`pytest tests/test_part_b.py`).
13. Compile reports, update `README.md` and `requirements.txt`.
