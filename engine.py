import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from GA.engine import GA_Engine
from GA.components.population import Population
from GA.components.individual import Individual
from GA.operators.selection import TournamentSelection
from GA.operators.crossover import UniformCrossover
from GA.operators.mutation import UniformMutation
from Data_Process.fx_data_entry import FX_data
from Strategy.MTS import Multi_Strategy
from Backtest.trade import Trade
import json
import pandas as pd

# Open dataset file
file_name = 'fitness_data.json'
fitness_file_path = parent_dir+"/"+file_name

if not os.path.isfile(file_name):
    a = {}
    b = json.dumps(a)
    f = open(file_name, 'w')
    f.write(b)
    f.close()

with open(file_name) as f:
    fitness_database = json.load(f)
    fitness_database = {tuple(map(float, k.strip('()').split(', '))): v for k, v in fitness_database.items()}

# Give the file path of data
file_path = "/Users/liuhsiaoching/Desktop/Dissertation/Data/Month/AUDJPY/AUDJPY_202106.csv"


# The data saver
global fx_data_saver
fx_data_saver = FX_data(file_path=file_path, 
                        currency_pair="EUR/GBP",
                        time="2021Q2")


# thres
thres = [0.002, 0.004, 0.005, 0.008]

# ru, rd (estimated ratio of OS to DC for each threshold)
estimated_r_mutiplier = [[3.7, 5.26],[2.87, 2.32],[2.86, 1.37],[3, 1.42]]


# initial asset
global trader
trader = {
    "cash": 8500000,
    "Q trade": 1
}

# chromosome = [a, b1, b2, w1, w2, w3, w4]
individual = Individual(ranges=[(0.1, 0.3), (0.4, 0.6), (0.7, 1), (0.1, 1), (0.1, 1), (0.1, 1), (0.1, 1)], round=2)
population = Population(individual=individual, size=10, fitness_database=fitness_database)
population.initialize()

selection = TournamentSelection(tournament_size=7)
crossover = UniformCrossover(crossover_rate=0.8, gene_exchange_rate=0.5)
mutation = UniformMutation(mutation_rate=0.1)


def fit_func(indv):
    dc_param = indv.chromosome[:-4]
    weight = indv.chromosome[-4:]
    strategy_paramters = dc_param + thres
    strategy = Multi_Strategy(fx_data_saver,
                            estimated_r_mutiplier, 
                            strategy_paramters)
    strategy.go_strategy(weight)

    t1 = Trade(fx_data_saver,
                   strategy,
                   trader)
    
    return t1.fitness

engine = GA_Engine(population=population, selection=selection,
                  crossover=crossover, mutation=mutation,
                  fitness_function=fit_func, database_path=fitness_file_path)

engine.run(35)

with open(file_name, 'w') as file:
    new_dict = {str(k): v for k, v in engine.population.fitness_database.items()}
    b = json.dumps(new_dict)
    f = open(file_name, 'w')
    f.write(b)
    f.close()


record_file = 'engine_record.json'
# Open dataset file
if not os.path.isfile(record_file):
    f = open(record_file, 'w')
    f.close()

with open(record_file) as f:
    b = json.dumps(engine.max_fitness_dict)
    f = open(record_file, 'w')
    f.write(b)
    f.close()

