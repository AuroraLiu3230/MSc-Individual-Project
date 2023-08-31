Contents
Backtest/
* `fitness.py`: Evaluates trade performance to calculate fitness score for GA
* `trade.py`: Executes backtesting for a trading strategy

Data_Process/
* Data cleaning scripts for preparing FX data

DC/
* `DC_Transformer.py`: Transforms time series data to intrinsic time series

GA/
* Genetic algorithm components, operators, and engine

Strategy/
* Implementations of various trading strategies, including benchmarks

Experiment/
* Output logs from experiments


Usage
1. Use `calc_r.py` to estimate r ratios for dataset and thresholds
2. Run `engine.py` to find optimal parameters for DC strategies via GA
3. Run `backtesting.py` to backtest optimized strategies on data
