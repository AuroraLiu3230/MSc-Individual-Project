import os
from Backtest.trade import Trade
import csv

class RecordFuction:
    def __init__(self, trader, parameters, strategy) -> None:
        self.parameters = parameters
        self.s = strategy
        self.dataName = self.s.dataName
        self.t = Trade(strategy=strategy, trader=trader)
        self.pnl = self.t.pnl
        self.return_rate = self.t.return_rate
        self.varNames = list(parameters.keys())[:5]

        weights = []
        for i in range(len(parameters['weights'])):
            weights.append("w"+str(i+1))

        self.varNames += weights

        self.colNames = self.varNames + ["PnL", "Return"]


        self.record_EUR_GBP()


        
    def record_EUR_GBP(self):

        data_dict = {}

        for i in range(5):
            data_dict[self.colNames[i]] = self.parameters[self.colNames[i]]
        
        for i in range(5, len(self.varNames)):
            data_dict[self.colNames[i]] = self.parameters['weights'][i-5]

        data_dict[self.colNames[-2]] = self.t.pnl
        data_dict[self.colNames[-1]] = self.t.return_rate

        file_exists = os.path.exists("EUR_GBP.csv")
        with open("EUR_GBP.csv", mode="w+", encoding="big5", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.colNames, delimiter=",")
            if not file_exists:
                writer.writeheader()
            writer.writerow(data_dict)





