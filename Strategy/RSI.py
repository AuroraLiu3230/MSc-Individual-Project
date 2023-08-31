import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


from typing import Dict, List
import pandas as pd
import numpy as np


class RSI:
    """
    A simple DC-based strategy for FX trading.

    @param {dict} [.FX_data]: The saver of raw data.
    @param {list} [estimated_r_mutilplier]: [ru, rd]
    @param {list} [strategy_parameters]: [b1, b2, threshold]
    """
    def __init__(self, data_saver) -> None:
        self.data = data_saver.data
        self.dataName = data_saver.data_name
        self.nTimeSteps = data_saver.nTimeSteps

        self.STRATEGY_CODE = {
            -1: "sell",
            0: "hold",
            1: "buy"
        }

        self.go_strategy()
        
    def go_strategy(self):

        self.trade_strategy: Dict[List] = {
            "strategy": [0]*self.nTimeSteps,
            "Q rate": [0]*self.nTimeSteps
            }
        
        self.trade_strategy['strategy'][0] = 1
        self.trade_strategy["Q rate"][0] = 1

        self.trade_strategy['strategy'][-1] = -1
        self.trade_strategy["Q rate"][-1] = 1
        stock_data = pd.DataFrame()

        stock_data['price'] = pd.DataFrame(self.data.Mid)
        stock_data['diff'] = stock_data['price'].diff()
        stock_data['up'] = stock_data['diff'].clip(lower=0)
        stock_data['down'] = (-1) * stock_data['diff'].clip(upper=0)

        stock_data['up_mean'] = stock_data['up'].ewm(com=100, adjust=False).mean()
        stock_data['down_mean'] = stock_data['down'].ewm(com=100, adjust=False).mean()

        stock_data['RS'] = stock_data['up_mean'] / stock_data['down_mean']
        stock_data['RSI'] = stock_data['RS'].apply(lambda rs: rs/(1+rs) * 100)

        for i in range(len(stock_data)):
            if stock_data.loc[i, 'RSI'] <= 30 and stock_data.loc[i-1, 'RSI'] > stock_data.loc[i, 'RSI']:
                self.trade_strategy['strategy'][i] = 1
                self.trade_strategy['Q rate'][i] = 1
            elif stock_data.loc[i, 'RSI'] >= 70 and stock_data.loc[i-1, 'RSI'] < stock_data.loc[i, 'RSI']:
                self.trade_strategy['strategy'][i] = -1
                self.trade_strategy['Q rate'][i] = 1

        df = pd.DataFrame(self.trade_strategy)
        df = df[df.index <= self.data.index[-1]]
        self.all_action_df = df
        self.strategy_df = df[df['Q rate']!=0]


    
