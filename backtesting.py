import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Data_Process.fx_data_entry import FX_data
from Strategy.MTS import MTS
from Strategy.BandH import BandH
from Strategy.MACD import MACD
from Strategy.RSI import RSI
from Strategy.STS import STS
from Backtest.trade import Trade
import pandas as pd

"""
Parameters
"""
evalution_dict = {}
estimated_param = [0.3, 0.6, 1, 0.002, 0.004, 0.005, 0.008]
weight=[1, 1, 1, 1]
param = [0.3, 0.6, 1] # a, b1, b2
threshold_ls = [0.002, 0.004, 0.005, 0.008]



i=1

for currency in ["AUDJPY", "EURNZD", "USDCAD"]:
    if currency == "AUDJPY":
        test_currency = "AUDJPY" # e.g. AUDJPY
        data_ls = ["AUDJPY_202107","AUDJPY_202108","AUDJPY_202109","AUDJPY_202110","AUDJPY_202111","AUDJPY_202112","AUDJPY_202201","AUDJPY_202202","AUDJPY_202203","AUDJPY_202204","AUDJPY_202205",'AUDJPY_202206']
        budget = 9500000
        estimated_r_mutiplier = [[3.7, 5.26],[2.87, 2.32],[2.86, 1.37],[3, 1.42]]

        estimated_param_2 = [0.29, 0.59, 0.73, 0.002, 0.004, 0.005, 0.008]
        weight_2=[0.68, 0.14, 0.83, 0.56]
    
    elif currency == "EURNZD":
        test_currency = "EURNZD" # e.g. AUDJPY
        data_ls = ["EURNZD_202107","EURNZD_202108","EURNZD_202109","EURNZD_202110","EURNZD_202111","EURNZD_202112","EURNZD_202201","EURNZD_202202","EURNZD_202203","EURNZD_202204","EURNZD_202205",'EURNZD_202206']
        budget = 180000
        estimated_r_mutiplier = [[3.11, 5.58], [2.29, 5.58], [2.21, 2.20], [3,45, 1.61]]

        estimated_param_2 = [0.29, 0.46, 0.71, 0.002, 0.004, 0.005, 0.008]
        weight_2=[0.29, 0.41, 0.12, 0.94]
    
    elif currency == "USDCAD":
        test_currency = "USDCAD" # e.g. AUDJPY
        data_ls = ["USDCAD_202107","USDCAD_202108","USDCAD_202109","USDCAD_202110","USDCAD_202111","USDCAD_202112","USDCAD_202201","USDCAD_202202","USDCAD_202203","USDCAD_202204","USDCAD_202205",'USDCAD_202206']
        budget = 150000
        estimated_r_mutiplier = [[3.02, 4.81], [2.22, 4.72], [2.79, 2.14], [2.21, 2.14]]

        estimated_param_2 = [0.3, 0.6, 0.75, 0.002, 0.004, 0.005, 0.008]
        weight_2 = [0.75, 0.96, 0.14, 0.78]

    # initial asset
    trader = {
        "cash": budget,
        "Q trade": 1
    }

    for data in data_ls:
        file_path = "/Users/liuhsiaoching/Desktop/Dissertation/Data/Month/"+test_currency+"/" + data + ".csv"


        time = data[-6:]
        # The data saver
        fx_data_saver = FX_data(file_path=file_path, 
                                currency_pair=test_currency,
                                time=time)
        
        """
        Buy and Hold
        """
        buy_and_hold = BandH(fx_data_saver)

        t1 = Trade(fx_data_saver, buy_and_hold, trader)
        t1.backtest()
        df = pd.DataFrame(t1.pnl_record)
        evalution_dict[str(i)] = [test_currency, "B&H", time, "None",
                                t1.total_pnl,t1.fitness,
                                t1.total_return, 
                                t1.std_dev_returns, 
                                t1.max_drawdown, t1.win_rate, len(df)]
        i += 1

        """
        RSI
        """
        rsi = RSI(fx_data_saver)

        t1 = Trade(fx_data_saver, rsi, trader)
        t1.backtest()
        df = pd.DataFrame(t1.pnl_record)
        evalution_dict[str(i)] = [test_currency, "RSI", time, "None",
                                t1.total_pnl,t1.fitness,
                                t1.total_return, 
                                t1.std_dev_returns, 
                                t1.max_drawdown, t1.win_rate, len(df)]
        i += 1

        """
        MACD
        """
        macd = MACD(fx_data_saver)

        t1 = Trade(fx_data_saver, macd, trader)
        t1.backtest()
        df = pd.DataFrame(t1.pnl_record)
        evalution_dict[str(i)] = [test_currency, "MACD", time, "None",
                                t1.total_pnl,t1.fitness,
                                t1.total_return, 
                                t1.std_dev_returns, 
                                t1.max_drawdown, t1.win_rate, len(df)]
        i += 1

        """
        STS
        """
        j = 0
        for thres in threshold_ls:
            sts = STS(fx_data_saver,
                    estimated_r_mutiplier[j],
                    param + [thres])

            t1 = Trade(fx_data_saver, sts, trader)
            t1.backtest()
            df = pd.DataFrame(t1.pnl_record)
            evalution_dict[str(i)] = [test_currency, "STS", time, thres,
                                    t1.total_pnl,t1.fitness,
                                    t1.total_return, 
                                    t1.std_dev_returns, 
                                    t1.max_drawdown, t1.win_rate, len(df)]
            i+=1; j+=1

        """
        MTS
        """
        TS1_multi = MTS(fx_data_saver, estimated_r_mutiplier, estimated_param)
        TS1_multi.go_strategy(weight)
        t1 = Trade(fx_data_saver, TS1_multi, trader)
        t1.backtest()
        df = pd.DataFrame(t1.pnl_record)
        evalution_dict[str(i)] = [test_currency, "MTS", time, "All",
                                t1.total_pnl,t1.fitness,
                                t1.total_return, 
                                t1.std_dev_returns, 
                                t1.max_drawdown, t1.win_rate, len(df)]
        
        i+=1
        """
        MTSGA
        """
        TS1_multi = MTS(fx_data_saver, estimated_r_mutiplier, estimated_param_2)
        TS1_multi.go_strategy(weight_2)
        t1 = Trade(fx_data_saver, TS1_multi, trader)
        t1.backtest()
        df = pd.DataFrame(t1.pnl_record)
        evalution_dict[str(i)] = [test_currency, "MTSGA", time, "All",
                                t1.total_pnl,t1.fitness,
                                t1.total_return, 
                                t1.std_dev_returns, 
                                t1.max_drawdown, t1.win_rate, len(df)]
        i+=1

    evalution_df = pd.DataFrame(evalution_dict, index=["Currency","Strategy",
                                                    "Time","Threshold",
                                                    'PnL','Fitness', 
                                                    'TR',  
                                                    'std(RR)', 
                                                    'MDD' ,'Win Rate','nTrade'])

evalution_df.to_csv('Backtest.csv')