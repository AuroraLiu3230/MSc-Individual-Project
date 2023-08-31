import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Backtest.fitness import FitnessCalculator
from typing import Dict, List
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

class Trade:
    def __init__(self, data_saver, strategy, trader:Dict) -> None:
        # raw data
        self.data = data_saver.data
        self.timelist = data_saver.timelist         # {list}
        self.time_last_idx = len(self.timelist)-1

        # strategy
        self.strategy_df = strategy.strategy_df     # {pd.dataframe["strategy", "Q rate"]} 

        # trader 
        self.cash = trader['cash']  # {int}
        self.Q = trader['Q trade']  # {int}

        self.meta_data()
        self.go_trade()

    def meta_data(self):
        """
        Initialize the data saving dictionary.
        """

        # Inventory Records
        self.inv_record: Dict[str, int] = {
            "Base": self.cash,
            "Quote": 0,
            "Lots": 0,
        }

        # Profit and Loss Records
        self.pnl_record: Dict[str, List] = {
            "Lots": [],
            "Open Time": [],
            "Close Time": [],
            "Open Price": [],
            "Close Price": [],
            "Pips": [],
            "PnL": [],
            "Duration": [],
            "Return": []
        }

        self.trade_point : Dict = {
            'long' : [],
            'long_price': [],
            'short' : [],
            'short_price':[]
        }

    def order(self, index:int, trade_type:str, quantity:int):
        """
        Send a buy (or sell) order
        """
        # Get the time of the trade
        time = self.timelist[index]

        # Determine the ask and bid prices based on trade type
        ask_price = self.data["Ask"][index]
        bid_price = self.data["Bid"][index]
        
        # Calculate the transaction price based on trade type
        transaction_price = ask_price if trade_type == "Long" else bid_price    

        order_dict = {
            "Index": index,
            "Time": time,
            "Type": trade_type,
            "Price": transaction_price,
            "Quantity": quantity
        }

        if trade_type == 'Long':
            self.trade_point['long'].append(index)
            self.trade_point['long_price'].append(transaction_price)
        
        if trade_type == 'Short':
            self.trade_point['short'].append(index)
            self.trade_point['short_price'].append(transaction_price)

        return order_dict


    def record_pnl(self, order):
        """
        Record profit and loss when a trade cycle completed

        self.pnl_record: Dict[str, List] = {
            "Lots": [],
            "Open Time": [],
            "Close Time": [],
            "Open Price": [],
            "Close Price": [],
            "Pips": [],
            "PnL": [],
            "Duration": [],
            "Return": []
        }
        """
        if order['Type'] == "Long":
            self.pnl_record['Open Time'].append(order['Time'])
            self.pnl_record['Open Price'].append(order['Price'])
            self.pnl_record['Lots'].append(order['Quantity'])

        elif order['Type'] == "Short":
            self.pnl_record['Close Time'].append(order['Time'])
            self.pnl_record['Close Price'].append(order['Price'])
            close_price = self.pnl_record['Close Price'][-1]
            open_price = self.pnl_record['Open Price'][-1]
            self.pnl_record['Pips'].append(close_price - open_price)

            open_time = self.pnl_record['Open Time'][-1]
            close_time = self.pnl_record['Close Time'][-1]
            self.pnl_record['Duration'].append(close_time-open_time)
            self.pnl_record['PnL'].append((close_price-open_price) * 100000 * order['Quantity'])
            self.pnl_record['Return'].append((close_price-open_price)/open_price)

    def record_inv(self, order):
        """
        Update current inventory
        """
        index = order['Index']
        trade_type = order["Type"]
        price = order["Price"]
        quantity = order["Quantity"]

        if trade_type == "Long":
            self.inv_record["Lots"] += quantity
            self.inv_record['Base'] -= price * quantity * 100000
            self.inv_record['Quote'] += quantity * 100000

        elif trade_type == "Short":
            self.inv_record["Lots"] -= quantity
            self.inv_record['Base'] += price * quantity * 100000
            self.inv_record['Quote'] -= quantity * 100000
   
    def record_transaction(self, order):
        self.record_pnl(order)
        self.record_inv(order)

    def go_trade(self):
        
        for idx in self.strategy_df.index :  # index when the strategy support to take action

            # Current Inventory State
            self.base = self.inv_record["Base"]; 
            self.quote = self.inv_record["Quote"]

            # Action price and quantity
            buy_price = self.data['Ask'][idx]
            sell_price = self.data['Bid'][idx]

            if idx == len(self.timelist)-1: # when the trading period ended
                quantity = self.inv_record["Lots"] # Short all quotes in hand
            else:
                quantity = self.Q * self.strategy_df['Q rate'][idx]

            #
            # Make Decision
            # 

            # Long
            if (self.strategy_df["strategy"][idx] == 1) and (buy_price * quantity * 100000 <= self.base) and (self.inv_record['Lots']==0):
                self.base -= buy_price * quantity * 100000
                self.quote +=  quantity * 100000
                buy_order = self.order(index=idx, trade_type="Long", quantity=quantity)
                self.record_transaction(buy_order)
                self.buy_idx = idx
                
            
            # Short
            elif (self.strategy_df["strategy"][idx] == -1) and (self.quote > 0) and (self.inv_record['Lots']!=0):
                if ((self.data.iloc[idx]['Time'] - self.data.iloc[self.buy_idx]['Time']).seconds >= 60*10):
                    self.base += sell_price * quantity * 100000
                    self.quote -= quantity * 100000
                    sell_order = self.order(index=idx, trade_type="Short", quantity=quantity)
                    self.record_transaction(sell_order)
                    self.buy_idx = None
        
        # Current Inventory State
        self.base = self.inv_record["Base"]; 
        self.quote = self.inv_record["Quote"]
            

    def backtest(self):
        self.trade_data = pd.DataFrame(self.pnl_record)

        # First, let's convert the Open Time and Close Time columns to datetime format
        # self.trade_data['Open Time'] = pd.to_datetime(self.trade_data['Open Time'], format="%Y%m%d %H%M%S%f")
        # self.trade_data['Close Time'] = pd.to_datetime(self.trade_data['Close Time'], format="%Y%m%d %H%M%S%f")

        # Total Profit/Loss
        self.total_pnl = round(self.trade_data['PnL'].sum(),4)

        # Average Profit/Loss per trade
        self.average_pnl_per_trade = round(self.trade_data['PnL'].mean(),4)

        # Win Rate
        self.win_rate = round((self.trade_data['PnL'] > 0).mean(),4)

        # Average Duration of Trades
        self.average_duration = pd.to_timedelta(self.trade_data['Duration']).mean()

        # Total Return
        self.total_return = round(self.trade_data['Return'].sum(),4)

        # Average Return per Trade
        self.average_return_per_trade = round(self.trade_data['Return'].mean(),4)
        
        # Get the returns 
        self.returns = self.trade_data['Return'],

        # # Maximum Drawdown
        mdd_rate = 0
        cash = self.cash
        for pnl_idx in range(len(self.pnl_record['Open Time'])):
            open_idx = self.data[self.data.Time==self.pnl_record['Open Time'][pnl_idx]].index[0]
            close_idx = self.data[self.data.Time==self.pnl_record['Close Time'][pnl_idx]].index[0]
            cash -= self.pnl_record['Open Price'][pnl_idx]*self.pnl_record['Lots'][pnl_idx]*100000
            
            df = self.data.loc[open_idx:close_idx][['Mid']]
            df['Value'] = df['Mid']*self.pnl_record['Lots'][pnl_idx]*100000 + cash
            
            portfolio_value = df['Value']
            dd_value = portfolio_value.cummax() - portfolio_value
            dd_rate = dd_value / (dd_value + portfolio_value)

            if dd_rate.max()>mdd_rate:
                mdd_rate = dd_rate.max()

            cash += self.pnl_record['Close Price'][pnl_idx]*self.pnl_record['Lots'][pnl_idx]*100000

        if math.isnan(mdd_rate):
            self.max_drawdown = 0

        else:
            self.max_drawdown = round(mdd_rate, 4)


        
        # Profit Factor
        gross_profit = self.trade_data['PnL'][self.trade_data['PnL'] > 0].sum()
        gross_loss = self.trade_data['PnL'][self.trade_data['PnL'] < 0].sum()
        self.profit_factor = round(gross_profit / abs(gross_loss),4)

        # Standard Deviation of Returns
        self.std_dev_returns = round(self.trade_data['Return'].std(),4)

        # Fitness
        calculator = FitnessCalculator(self.total_return, self.max_drawdown)
        self.fitness = calculator.calculate_fitness()

    
    def evaluate(self):
        dict = {
            "PnL": self.total_pnl,
            "Profit Factor": self.profit_factor,
            "Total Return Rate": self.total_return,
            "Stv of Return": self.std_dev_returns,
            "Maximum Drawdown": self.max_drawdown,
            "Win Rate": self.win_rate,
            "Avg Duration": self.average_duration,
            "Trade times": len(pd.DataFrame(self.pnl_record))
        }

        self.evaluate_matrix = pd.DataFrame([dict])
        

    def plot(self, type=None):
        # Plot of cumulative returns
        plt.figure(figsize=(10,6))
        plt.plot(self.trade_data['Close Time'], self.trade_data['Return'].cumsum())
        plt.xlabel('Time')
        plt.ylabel('Cumulative Returns')
        plt.title('Cumulative Returns Over Time')
        plt.grid(True)
        plt.show()

        # Plot of drawdowns
        plt.figure(figsize=(10,6))
        plt.plot(self.trade_data['Close Time'], self.drawdown)
        plt.xlabel('Time')
        plt.ylabel('Drawdown')
        plt.title('Drawdown Over Time')
        plt.grid(True)
        plt.show()

        # Histogram of returns
        plt.figure(figsize=(10,6))
        plt.hist(self.returns, bins=50, alpha=0.75)
        plt.xlabel('Return')
        plt.ylabel('Frequency')
        plt.title('Histogram of Returns')
        plt.grid(True)
        plt.show()

        # Plot the bid price over time
        self.data.index = self.data['Time']
        plt.figure(figsize=(10,6))
        plt.plot(self.data.index, self.data['Mid'], label='Price')

        # Mark the open positions
        open_positions = self.trade_data['Open Time']
        plt.scatter(open_positions, self.data.loc[open_positions]['Mid'], color='g', marker='^', label='Open Position')

        # Mark the close positions
        close_positions = self.trade_data['Close Time']
        plt.scatter(close_positions, self.data.loc[close_positions]['Mid'], color='r', marker='v', label='Close Position')

        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('Price with Trading Positions')
        plt.legend()
        plt.grid(True)
        plt.show()
