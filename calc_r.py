import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Data_Process.fx_data_entry import FX_data
from Strategy.STS import STS
import numpy as np


data_ls = ["AUDJPY_202101","AUDJPY_202102","AUDJPY_202103","AUDJPY_202104","AUDJPY_202105","AUDJPY_202106"]
thres_ls = [0.002, 0.004, 0.005, 0.008]


# ru, rd
estimated_r_mutiplier = [2, 2]

# ru_arr_all, rd_arr_all
ru_arr_all = np.array([]); rd_arr_all = np.array([])

ru_arr_2 = np.array([]); rd_arr_2 = np.array([])

ru_arr_4 = np.array([]); rd_arr_4 = np.array([])

ru_arr_5 = np.array([]); rd_arr_5 = np.array([])

ru_arr_8 = np.array([]); rd_arr_8 = np.array([])


# ru_ls, rd_ls
ru_ls = []; rd_ls = []

for data in data_ls:
    
    file_path = "/Users/liuhsiaoching/Desktop/Dissertation/Data/Month/AUDJPY/" + data + ".csv"

    for thres in thres_ls:
        # The data saver
        fx_data_saver = FX_data(file_path=file_path, 
                                currency_pair="AUDJPY",
                                time="202106")

        # a, b1, b2, thres
        strategy_paramters = [0.3, 0.6, 0.9] + [thres]


        single_strategy = STS(fx_data_saver, 
                                estimated_r_mutiplier, 
                                strategy_paramters)
        
        if thres == 0.002:
            ru_arr_2 = np.append(ru_arr_2, single_strategy.t.ru_ls)
            rd_arr_2 = np.append(rd_arr_2, single_strategy.t.rd_ls)

        elif thres == 0.004:
            ru_arr_4 = np.append(ru_arr_4, single_strategy.t.ru_ls)
            rd_arr_4 = np.append(rd_arr_4, single_strategy.t.rd_ls)

        elif thres == 0.005:
            ru_arr_5 = np.append(ru_arr_5, single_strategy.t.ru_ls)
            rd_arr_5 = np.append(rd_arr_5, single_strategy.t.rd_ls)

        elif thres == 0.008:
            ru_arr_8 = np.append(ru_arr_8, single_strategy.t.ru_ls)
            rd_arr_8 = np.append(rd_arr_8, single_strategy.t.rd_ls)

        ru_arr_all = np.append(ru_arr_all, single_strategy.t.ru_ls)
        rd_arr_all = np.append(rd_arr_all, single_strategy.t.rd_ls)


ru_ls = [np.mean(ru_arr_2),np.mean(ru_arr_4),np.mean(ru_arr_5),np.mean(ru_arr_8),np.mean(ru_arr_all)]
rd_ls = [np.mean(rd_arr_2),np.mean(rd_arr_4),np.mean(rd_arr_5),np.mean(rd_arr_8),np.mean(rd_arr_all)]