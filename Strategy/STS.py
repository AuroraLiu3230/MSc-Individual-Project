import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from DC.DC_Transformer import DC_Transformer
from typing import Dict, List
import pandas as pd
import numpy as np


class STS:
    """
    A simple DC-based strategy for FX trading.

    @param {dict} [.FX_data]: The saver of raw data.
    @param {list} [estimated_r_mutilplier]: [ru, rd]
    @param {list} [strategy_parameters]: [a, b1, b2, threshold]
    """
    def __init__(self, data_saver, estimated_r_mutiplier:List, strategy_parameters:List) -> None:
        self.data = data_saver.data
        self.dataName = data_saver.data_name
        self.ru = estimated_r_mutiplier[0]; self.rd = estimated_r_mutiplier[1]
        self.a = strategy_parameters[0]; self.b1 = strategy_parameters[1]; self.b2 = strategy_parameters[2]
        self.threshold= strategy_parameters[3]
        self.nTimeSteps = data_saver.nTimeSteps

        self.STRATEGY_CODE = {
            -1: "sell",
            0: "hold",
            1: "buy"
        }

        self.t = DC_Transformer(data_saver, tres=self.threshold)
        self.df = self.t.get_df()

        self.trade_strategy: Dict[List] = {
            "strategy": np.zeros(self.nTimeSteps),
            "Q rate": np.zeros(self.nTimeSteps)
            }

        self.go_strategy()
    
    def adjust_strategy(self, i: int, strategy: int, q_rate: int):
        """Adjust strategy and Q rate at the given index."""
        self.trade_strategy["strategy"][i] = strategy
        self.trade_strategy["Q rate"][i] = q_rate

    def _long_strategy(self, i:int):
        DC_length = self.t.lengths['DC_up'][self.index_up]
        self.tl_1 = int(i + DC_length * self.ru * self.a)
        self.ts_0 = int(i + DC_length * self.ru * self.b1)
        self.ts_1 = int(i + DC_length * self.ru * self.b2)
        self.adjust_strategy(i, 1, 1)
        self.PDCC = self.df['Mid'][i]
        self.index_up += 1
        self.index_buy = i

    def _short_strategy(self, i:int, s:int):
        if (self.ts_0 < i < self.ts_1) and  (s in [2, 100, -1]) and self.df['Mid'][i] >= self.PDCC*(1+0.8*self.threshold):
            self.adjust_strategy(i, -1, 1)

        if i > self.ts_1:
            self.adjust_strategy(i, -1, 1)
            
        if (s == -10) :
            self.adjust_strategy(i, -1, 1)
            self.PDCC = None

    def go_strategy(self):
        status = self.df['Status']

        self.index_up = 0
        
        self.PDCC = None

        for i, s in enumerate(status):

            if s == 10:
                self._long_strategy(i)

            elif self.PDCC is not None:
                if i <= self.tl_1 and s == 2:
                    self.adjust_strategy(i, 1, 1)
                else:
                    self._short_strategy(i, s)
        
        self.adjust_strategy(self.nTimeSteps-1, -1, 1)


        df = pd.DataFrame(self.trade_strategy)
        df = df[df.index <= self.data.index[-1]]
        self.all_action_df = df
        self.strategy_df = df[df['Q rate']!=0]
        


    
