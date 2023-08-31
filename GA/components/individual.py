from random import uniform
from copy import deepcopy

class Individual:
    """
    Base class for individuals

    @param {list of tuple} [ranges]: the acceptable range of values for each entry in the solution.
    """
    def __init__(self, ranges, round=2) -> None:
        self.ranges = ranges
        self.solution, self.chromosome = [], []
        self.fitness = None
        self.round = round

    def initialize(self, chromosome=None, database=None):
        """
        Initialize the individaul

        @param {list of float} [chromosome]: chromosome sequence for the individual
        """

        self.chromosome = chromosome if chromosome else self.random_chromosome()


    def random_chromosome(self):
        return [round(uniform(a,b), self.round) for (a, b) in self.ranges]

    
    def clone(self):
        """
        Clone a new individual from the current one.
        """
        cloned_ranges = deepcopy(self.ranges)
        cloned_chromosome = deepcopy(self.chromosome)
        cloned_individual = self.__class__(cloned_ranges)
        cloned_individual.initialize(chromosome=cloned_chromosome)

        return cloned_individual
    


