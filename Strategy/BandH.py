import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


from typing import Dict, List
import pandas as pd


class BandH:
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

        df = pd.DataFrame(self.trade_strategy)
        df = df[df.index <= self.data.index[-1]]
        self.all_action_df = df
        self.strategy_df = df[df['Q rate']!=0]


    
