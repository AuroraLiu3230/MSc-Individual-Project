from components.population import Population
from components.individual import Individual
from operators.selection import TournamentSelection
from operators.crossover import UniformCrossover
from operators.mutation import UniformMutation
from engine import GA_Engine
from math import sin, cos


individual = Individual(ranges=[(0,10)])
population = Population(individual=individual, size=50)
population.initialize()

selection = TournamentSelection(tournament_size=2)
crossover = UniformCrossover(crossover_rate=0.8, gene_exchange_rate=0.5)
mutation = UniformMutation(mutation_rate=0.1)

def fit_func(indv):
    x, = indv.chromosome
    return x + 10*sin(5*x) + 7*cos(4*x)

engine = GA_Engine(population=population, selection=selection,
                  crossover=crossover, mutation=mutation,
                  fitness_function=fit_func)