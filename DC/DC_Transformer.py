from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import pandas as pd
        
class DC_Transformer:
    def __init__(self, data_saver, tres=0.01) -> None:
        
        self.STATUS_CODE = {
            0: 'Extrema',
            100: "Maximum",
            -100: "Minimum",
            10: "Up DC",
            -10: "Down DC",
            1: "Up Trend",
            -1: "Down Trend",
            2: "Up OS",
            -2: "Down OS",
            3 : "No Info",
        }

        self.data = data_saver.data
        self.dataName = data_saver.data_name
        self.time = self.data['Time']
        self.mid = self.data['Mid']
        self.bid = self.data['Bid']
        self.ask = self.data['Ask']
        

        self.delta_up = tres
        self.delta_down = -tres
        
        # set-up metadata storages
        self.meta_data()

        self.transform()

        self.DC_OS_ratio()

    def meta_data(self):
        self.status: List[int] = []

        self.movements: Dict[str, List[float]] = {
            "DC_up": [],
            "DC_down": [],
            "OS_up": [],
            "OS_down": []
        }

        self.lengths: Dict[str, List[float]] = {
            "DC": [],
            "OS": [],
            "DC_up": [],
            "DC_down": [],
            "OS_up": [],
            "OS_down": []
        }

        self.ru_data: Dict = {
            'DC_price': [],
            'DC_length': [],
            'last_DC_price': [],
            'last_DC_length': [],
            'last_OS_length': [],
            'OS_length':[]
        }

        self.rd_data: Dict = {
            'DC_price': [],
            'DC_length': [],
            'last_DC_price': [],
            'last_DC_length': [],
            'last_OS_length': [],
            'OS_length':[]
        }

        

    def calc_return(self, x1, x2):
        "simple return"

        return (x2-x1) / x1
    
    def update_r_data(self, type, price, len):
        if type == 'ru':
            self.ru_data['DC_price'].append(price)
            self.ru_data['DC_length'].append(len)
        elif type == 'rd':
            self.rd_data['DC_price'].append(price)
            self.rd_data['DC_length'].append(len)

    def dissect_DC(self):
        mode = None

        for i, price in enumerate(self.mid):

            if i == 0:
                self.status.append(0)
                EXT_price = price
                EXT_idx = i
                continue

            if mode is None:
                r = self.calc_return(EXT_price, price)

                if r >= self.delta_up:
                    self.status[0] = -100
                    self.status.append(10)
                    self.status[(EXT_idx+1) : i] = [1] * (i - EXT_idx - 1)
                    last_DC_idx = i

                    self.movements['DC_up'].append(np.abs(r))

                    self.lengths['DC'].append(np.abs(i - 0 + 1))
                    self.lengths['DC_up'].append(np.abs(i - 0 + 1))

                    self.update_r_data('ru', price, np.abs(i - 0 + 1))

                    mode = 'bullish'
                    continue

                elif r <= self.delta_down:
                    self.status[0] = 100
                    self.status.append(-10)
                    self.status[(EXT_idx+1) : i] = [-1] * (i - EXT_idx - 1)
                    last_DC_idx = i

                    self.movements['DC_down'].append(np.abs(r))

                    self.lengths['DC'].append(np.abs(i - 0 + 1))
                    self.lengths['DC_down'].append(np.abs(i - 0 + 1))

                    self.update_r_data('rd', price, np.abs(i - 0 + 1))

                    mode = 'bearish'
                    continue

                self.status.append(3)

            if mode == 'bullish':
                if price >= EXT_price:
                    EXT_price = price
                    EXT_idx = i
                
                r = self.calc_return(EXT_price, price)

                if r <= self.delta_down:
                    self.status.append(-10)
                    mode = 'bearish'

                    self.status[EXT_idx] = 100
                    self.status[(EXT_idx+1) : i] = [-1] * (i - EXT_idx -1)

                    self.movements['DC_down'].append(np.abs(r))
                    self.movements['OS_up'].append(np.abs(self.calc_return(self.mid[last_DC_idx], self.mid[EXT_idx])))

                    self.lengths['DC'].append(np.abs(i - EXT_idx + 1))
                    self.lengths['OS'].append(np.abs(EXT_idx - last_DC_idx + 1))
                    self.lengths['DC_down'].append(np.abs(i - EXT_idx + 1))
                    self.lengths['OS_up'].append(np.abs(EXT_idx - last_DC_idx + 1))

                    self.update_r_data('rd', price, np.abs(i - EXT_idx + 1))

                    last_DC_idx = i
                    continue
                
                self.status.append(2)

            if mode == 'bearish':
                if price <= EXT_price:
                    EXT_price = price
                    EXT_idx = i
                
                r = self.calc_return(EXT_price, price)

                if r >= self.delta_up:
                    self.status.append(10)
                    mode = 'bullish'

                    self.status[EXT_idx] = -100
                    self.status[(EXT_idx+1) : i] = [1] * (i-EXT_idx-1)

                    self.movements['DC_up'].append(np.abs(r))
                    self.movements['OS_down'].append(np.abs(self.calc_return(self.mid[last_DC_idx], self.mid[EXT_idx])))

                    self.lengths['DC'].append(np.abs(i - EXT_idx + 1))
                    self.lengths['OS'].append(np.abs(EXT_idx - last_DC_idx + 1))
                    self.lengths['DC_up'].append(np.abs(i - EXT_idx + 1))
                    self.lengths['OS_down'].append(np.abs(EXT_idx - last_DC_idx + 1))

                    self.update_r_data('ru', price, np.abs(i - EXT_idx + 1))
                    
                    last_DC_idx = i
                    continue
                self.status.append(-2)
        
        self.ru_data['last_DC_price'] = [None] + self.ru_data['DC_price'][:-1]
        self.ru_data['last_DC_length'] = [None] + self.ru_data['DC_length'][:-1]
        self.ru_data['last_OS_length'] = [None] + self.lengths['OS_up'][:-1]
        self.ru_data['OS_length'] = self.lengths['OS_up']

        self.rd_data['last_DC_price'] = [None] + self.rd_data['DC_price'][:-1]
        self.rd_data['last_DC_length'] = [None] + self.rd_data['DC_length'][:-1]
        self.rd_data['last_OS_length'] = [None] + self.lengths['OS_down'][:-1]
        self.rd_data['OS_length'] = self.lengths['OS_down']
        
    def interpolation(self):
        marked_x = np.array(self.markers[1000][0]).astype(int)
        marked_y = np.array(self.markers[1000][1]).astype(float)

        if len(marked_y) >= 2:
            
            all_x = list(np.arange(len(self.mid)))

            inter_max_range = marked_x[-1]
            all_max_range = all_x[-1]
            out_of_range = np.arange(inter_max_range+1, all_max_range+1)

            # in-range interpolation
            inter_y = interp1d(marked_x, marked_y, kind='linear')
            temp = np.arange(inter_max_range+1)
            transformed_target = inter_y(temp)

            self.tdata = np.append(transformed_target, self.mid[out_of_range])
        
        else:
            self.tdata = self.mid
    
    def transform(self):
        
        self.sigma = round(np.std(np.diff(np.log(self.mid))), 6)

        self.dissect_DC()
        self.marker()
        self.interpolation()

    def DC_OS_ratio(self):

        # Calculate self.ru_ls based on lengths of 'DC_up' and 'OS_up'
        if len(self.lengths['DC_up']) > len(self.lengths['OS_up']):
            self.ru_ls = np.array(self.lengths['OS_up']) / np.array(self.lengths['DC_up'][:-1])
        else:
            self.ru_ls = np.array(self.lengths['OS_up']) / np.array(self.lengths['DC_up'])

        # Calculate self.rd_ls based on lengths of 'DC_down' and 'OS_down'
        if len(self.lengths['DC_down']) > len(self.lengths['OS_down']):
            self.rd_ls = np.array(self.lengths['OS_down']) / np.array(self.lengths['DC_down'][:-1])
        else:
            self.rd_ls = np.array(self.lengths['OS_down']) / np.array(self.lengths['DC_down'])

        # Calculate self.r, self.ru and self.rd 
        self.r = np.mean(np.hstack((self.ru_ls, self.rd_ls)))
        self.ru = np.mean(self.ru_ls)
        self.rd = np.mean(self.rd_ls)

    def marker(self) -> None:

        self.markers = {x: [] for x in self.STATUS_CODE.keys()}
        self.markers[1000] = []

        for i, s in enumerate(self.status):
            self.markers[s].append((i, self.mid[i]))
            
            if s in (0, 10, -10, 100, -100):
                self.markers[1000].append( (i, self.mid[i])) #Record the significant points (extrema and DC points)

        self.markers = {k: np.array(v).T for k, v in self.markers.items()}

    def make_plot(self) -> None:

        plt.figure(figsize = (10, 6))
        plt.plot(self.mid, label='raw data movement', color = 'black')
        plt.plot(self.tdata, lw=3, label='local extrema and directional changes', color='orange')
        
        marker_size = 5
        plt.plot(np.array(self.markers[100][0]).astype(int), np.array(self.markers[100][1]).astype(float), 'ro', markersize=marker_size, label = 'local maximum')
        plt.plot(np.array(self.markers[-100][0]).astype(int), np.array(self.markers[-100][1]).astype(float), 'ro', markersize=marker_size, label = 'local minimum')
        plt.plot(np.array(self.markers[10][0]).astype(int), np.array(self.markers[10][1]).astype(float), 'D', color='blue', markersize=marker_size, label = 'bullish directional change')
        plt.plot(np.array(self.markers[-10][0]).astype(int), np.array(self.markers[-10][1]).astype(float), 'D', color='blue', markersize=marker_size, label = 'bearish directional change')
        
        plt.xticks([])
        
        plt.xlabel('Time Index')
        plt.ylabel('Value')
        plt.title("%.2f %% Directional Change in %s"%(round(self.delta_up*100,2), self.dataName))
        plt.legend()
        plt.show()

    def get_data(self, DataName) -> np.array:

        if DataName == 'mid':
            return self.mid
        
        elif DataName == 'time':
            return self.time
        
        elif DataName == 'status':
            return self.status
        
    def get_df(self):
        df = pd.DataFrame(
            {
            "Time": self.time,
            "Bid": self.bid,
            "Ask": self.ask,    
            "Mid": self.mid,
            "DC Price": self.tdata,
            "Status": self.status
            }
            )
        return df



