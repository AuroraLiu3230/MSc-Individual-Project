import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from typing import Dict, List
from Strategy.STS import STS
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class MTS:
    """
    A simple DC-based strategy for FX trading.

    @param {dict} [.FX_data]: The saver of raw data.
    @param {list} [estimated_r_mutilplier]: [ru, rd]
    @param {list} [strategy_parameters]: [a, b1, b2, t1, t2, t3, t4]
    """

    def __init__(self, data_saver, estimated_r_mutiplier:List, strategy_parameters:List) -> None:
        self.data = data_saver.data
        self.dataName = data_saver.data_name
        self.a = strategy_parameters[0]; self.b1 = strategy_parameters[1]; self.b2 = strategy_parameters[2]

        params = []             # {List of Lists}
        for i in range(3, len(strategy_parameters)):
            param = strategy_parameters[:3] + [strategy_parameters[i]]
            params.append(param)

        strategies = []         # {List of Strategy}

        i=0
        for param in params:
            strategy = STS(data_saver, estimated_r_mutiplier[i], param)
            strategies.append(strategy)
            i+=1

        data = {}
        for i, strategy in enumerate(strategies, 1):
            column_name = f'S{i}'
            data[column_name] = strategy.all_action_df['strategy']
        
        self.df = pd.DataFrame(data) # {'S1','S2','S3','S4'}

    def go_strategy(self, weight_ls: List[float]) -> None:
        """
        @param {list} [weight_ls] : [w1, w2, w3, w4]
        """

        data = {f'S{i+1}': self.df[f'S{i+1}'] * weight_ls[i] for i in range(len(weight_ls))}
        data['D'] = sum(data.values())

        data = pd.DataFrame(data)

        def get_sign(value):
            if value > 0:
                return 1
            elif value < 0:
                return -1
            else:
                return 0
            
        data['strategy'] = data['D'].apply(get_sign)
        data['Q rate'] = [1 for i in range(len(data))]
        self.strategy_df = data[data['strategy']!=0]



