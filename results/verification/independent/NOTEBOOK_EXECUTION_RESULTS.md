
# Notebook Execution Results
- Total Notebooks: 24
- Executed Successfully: 19
- Status: `PARTIAL`
- Details:
- 01_data_collection.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\01_data_collection.ipynb)
- 02_data_cleaning.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\02_data_cleaning.ipynb)
- 02_data_collection.ipynb: FAIL (error code 1)
[NbConvertApp] Converting notebook notebooks\02_data_collection.ipynb to notebook
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\__main__.py", line 5, in <module>
    main()
    ~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\jupyter_core\application.py", line 284, in launch_instance
    super().launch_instance(argv=argv, **kwargs)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\traitlets\config\application.py", line 1080, in launch_instance
    app.start()
    ~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 420, in start
    self.convert_notebooks()
    ~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 597, in convert_notebooks
    self.convert_single_notebook(notebook_filename)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 563, in convert_single_notebook
    output, resources = self.export_single_notebook(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources, input_buffer=input_buffer
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 487, in export_single_notebook
    output, resources = self.exporter.from_filename(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources=resources
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\exporter.py", line 200, in from_filename
    with open(filename, encoding="utf-8") as f:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: 'notebooks\\02_data_collection.ipynb'

- 03_data_collection.ipynb: FAIL (error code 1)
[NbConvertApp] Converting notebook notebooks\03_data_collection.ipynb to notebook
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\__main__.py", line 5, in <module>
    main()
    ~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\jupyter_core\application.py", line 284, in launch_instance
    super().launch_instance(argv=argv, **kwargs)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\traitlets\config\application.py", line 1080, in launch_instance
    app.start()
    ~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 420, in start
    self.convert_notebooks()
    ~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 597, in convert_notebooks
    self.convert_single_notebook(notebook_filename)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 563, in convert_single_notebook
    output, resources = self.export_single_notebook(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources, input_buffer=input_buffer
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 487, in export_single_notebook
    output, resources = self.exporter.from_filename(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources=resources
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\exporter.py", line 200, in from_filename
    with open(filename, encoding="utf-8") as f:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: 'notebooks\\03_data_collection.ipynb'

- 03_exploratory_analysis.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\03_exploratory_analysis.ipynb)
- 04_data_collection.ipynb: FAIL (error code 1)
[NbConvertApp] Converting notebook notebooks\04_data_collection.ipynb to notebook
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\__main__.py", line 5, in <module>
    main()
    ~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\jupyter_core\application.py", line 284, in launch_instance
    super().launch_instance(argv=argv, **kwargs)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\traitlets\config\application.py", line 1080, in launch_instance
    app.start()
    ~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 420, in start
    self.convert_notebooks()
    ~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 597, in convert_notebooks
    self.convert_single_notebook(notebook_filename)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 563, in convert_single_notebook
    output, resources = self.export_single_notebook(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources, input_buffer=input_buffer
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 487, in export_single_notebook
    output, resources = self.exporter.from_filename(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources=resources
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\exporter.py", line 200, in from_filename
    with open(filename, encoding="utf-8") as f:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: 'notebooks\\04_data_collection.ipynb'

- 04_market_structure.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\04_market_structure.ipynb)
- 05_data_collection.ipynb: FAIL (error code 1)
[NbConvertApp] Converting notebook notebooks\05_data_collection.ipynb to notebook
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\__main__.py", line 5, in <module>
    main()
    ~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\jupyter_core\application.py", line 284, in launch_instance
    super().launch_instance(argv=argv, **kwargs)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\traitlets\config\application.py", line 1080, in launch_instance
    app.start()
    ~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 420, in start
    self.convert_notebooks()
    ~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 597, in convert_notebooks
    self.convert_single_notebook(notebook_filename)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 563, in convert_single_notebook
    output, resources = self.export_single_notebook(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources, input_buffer=input_buffer
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 487, in export_single_notebook
    output, resources = self.exporter.from_filename(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources=resources
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\exporter.py", line 200, in from_filename
    with open(filename, encoding="utf-8") as f:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
PermissionError: [Errno 13] Permission denied: 'notebooks\\05_data_collection.ipynb'

- 05_feature_engineering.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\05_feature_engineering.ipynb)
- 06_strategy_research.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\06_strategy_research.ipynb)
- 07_machine_learning.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\07_machine_learning.ipynb)
- 08_deep_learning.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\08_deep_learning.ipynb)
- 09_ensemble_learning.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\09_ensemble_learning.ipynb)
- 10_strategy_optimization.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\10_strategy_optimization.ipynb)
- 11_backtesting.ipynb: FAIL (error code 1)
[NbConvertApp] Converting notebook notebooks\11_backtesting.ipynb to notebook
C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\zmq\_future.py:718: RuntimeWarning: Proactor event loop does not implement add_reader family of methods required for zmq. Registering an additional selector thread for add_reader support via tornado. Use `asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())` to avoid this warning.
  self._get_loop()
[IPKernelApp] WARNING | Kernel is running over TCP without encryption. All communication (including code and outputs) is sent in plain text and is susceptible to eavesdropping. Use IPC transport or launch with kernel manager-provisioned CurveZMQ keys to enable transport encryption.
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\__main__.py", line 5, in <module>
    main()
    ~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\jupyter_core\application.py", line 284, in launch_instance
    super().launch_instance(argv=argv, **kwargs)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\traitlets\config\application.py", line 1080, in launch_instance
    app.start()
    ~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 420, in start
    self.convert_notebooks()
    ~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 597, in convert_notebooks
    self.convert_single_notebook(notebook_filename)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 563, in convert_single_notebook
    output, resources = self.export_single_notebook(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources, input_buffer=input_buffer
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\nbconvertapp.py", line 487, in export_single_notebook
    output, resources = self.exporter.from_filename(
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        notebook_filename, resources=resources
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\exporter.py", line 201, in from_filename
    return self.from_file(f, resources=resources, **kw)
           ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\exporter.py", line 220, in from_file
    return self.from_notebook_node(
           ~~~~~~~~~~~~~~~~~~~~~~~^
        nbformat.read(file_stream, as_version=4), resources=resources, **kw
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\notebook.py", line 36, in from_notebook_node
    nb_copy, resources = super().from_notebook_node(nb, resources, **kw)
                         ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\exporter.py", line 154, in from_notebook_node
    nb_copy, resources = self._preprocess(nb_copy, resources)
                         ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\exporters\exporter.py", line 353, in _preprocess
    nbc, resc = preprocessor(nbc, resc)
                ~~~~~~~~~~~~^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\preprocessors\base.py", line 48, in __call__
    return self.preprocess(nb, resources)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\preprocessors\execute.py", line 103, in preprocess
    self.preprocess_cell(cell, resources, index)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbconvert\preprocessors\execute.py", line 124, in preprocess_cell
    cell = self.execute_cell(cell, index, store_history=True)
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\jupyter_core\utils\__init__.py", line 165, in wrapped
    return loop.run_until_complete(inner)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^
  File "C:\Python314\Lib\asyncio\base_events.py", line 720, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbclient\client.py", line 1062, in async_execute_cell
    await self._check_raise_for_error(cell, cell_index, exec_reply)
  File "C:\Users\ASUS\desktop\gold_chart\.venv\Lib\site-packages\nbclient\client.py", line 918, in _check_raise_for_error
    raise CellExecutionError.from_cell_and_msg(cell, exec_reply_content)
nbclient.exceptions.CellExecutionError: An error occurred while executing the following cell:
------------------
import sys, os
import pandas as pd
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join('..', 'src')))

from backtest_engine import BacktestEngine
from strategy_engine import StrategyEngine

df = pd.read_parquet('../data/features/xauusd_features.parquet')
df_signals = StrategyEngine.generate_signals(df)

bt = BacktestEngine(config={"risk_reward": 2.0, "spread": 0.20, "slippage": 0.05, "commission": 0.02})
results = bt.run_backtest(market_df=df, feature_df=df, signal_df=df_signals[['signal']])
print("Backtest Summary:", results.get("summary"))

------------------


[31m---------------------------------------------------------------------------[39m
[31mUnboundLocalError[39m                         Traceback (most recent call last)
[36mCell[39m[36m [39m[32mIn[1][39m[32m, line 13[39m
[32m      9[39m df = pd.read_parquet([33m'../data/features/xauusd_features.parquet'[39m)
[32m     10[39m df_signals = StrategyEngine.generate_signals(df)
[32m     11[39m 
[32m     12[39m bt = BacktestEngine(config={[33m"risk_reward"[39m: [32m2.0[39m, [33m"spread"[39m: [32m0.20[39m, [33m"slippage"[39m: [32m0.05[39m, [33m"commission"[39m: [32m0.02[39m})
[32m---> [39m[32m13[39m results = bt.run_backtest(market_df=df, feature_df=df, signal_df=df_signals[[[33m'signal'[39m]])
[32m     14[39m print([33m"Backtest Summary:"[39m, results.get([33m"summary"[39m))

[36mFile [39m[32m~\desktop\gold_chart\src\backtest_engine.py:92[39m, in [36mBacktestEngine.run_backtest[39m[34m(self, market_df, feature_df, signal_df, models)[39m
[32m     90[39m                 outcome = [33m"[39m[33mLOSS[39m[33m"[39m
[32m     91[39m     [38;5;28;01mif[39;00m exit_price [38;5;129;01mis[39;00m [38;5;28;01mNone[39;00m:
[32m---> [39m[32m92[39m         exit_price = [30;43mnext_price[39;49m
[32m     93[39m     trades.append({
[32m     94[39m         [33m"[39m[33mtimestamp[39m[33m"[39m: idx,
[32m     95[39m         [33m"[39m[33mdirection[39m[33m"[39m: signal,
[32m   (...)[39m[32m     99[39m         [33m"[39m[33mrisk_reward[39m[33m"[39m: [38;5;28mself[39m.risk_reward,
[32m    100[39m     })
[32m    101[39m trade_log = pd.DataFrame(trades)

[31mUnboundLocalError[39m: cannot access local variable 'next_price' where it is not associated with a value


- 12_walk_forward_validation.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\12_walk_forward_validation.ipynb)
- 13_confidence_calibration.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\13_confidence_calibration.ipynb)
- 14_efficiency_prediction.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\14_efficiency_prediction.ipynb)
- 15_limit_entry_prediction.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\15_limit_entry_prediction.ipynb)
- 16_realtime_data_engine.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\16_realtime_data_engine.ipynb)
- 17_realtime_prediction.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\17_realtime_prediction.ipynb)
- 18_paper_trading.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\18_paper_trading.ipynb)
- 19_final_performance_report.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\19_final_performance_report.ipynb)
- 20_self_improvement_engine.ipynb: PASS (executed successfully, output saved to results\verification\executed_notebooks\20_self_improvement_engine.ipynb)
