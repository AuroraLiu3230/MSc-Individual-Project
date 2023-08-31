from .individual import Individual
from typing import List

class Population:
    """
    Class that representing population in genetic algorithm

    @param {obj: Individual} [individual] A template individual to serve as a blueprint 
                                        for cloning all the other individuals in the 
                                        current population, ensuring consistency in 
                                        their structure and characteristics.
    @param {int} [size] The number of individuals in population.
    """
    def __init__(self, individual, size=100, fitness_database=None) -> None:
        self.size = size
        self.individual_template = individual
        self.individuals: List[Individual]  = []
        self.fitness_database = fitness_database or {}
        self.max_fitness = None

    def initialize(self,
                   inidividuals: List[Individual] = None):
        IndividualType = self.individual_template.__class__

        if inidividuals is None:
            for _ in range(self.size):
                individual = IndividualType(ranges=self.individual_template.ranges, round=self.individual_template.round)
                individual.initialize()
                self.individuals.append(individual)

        else:
            self.individuals = inidividuals
        return self
    
    # @MemoizedProperty
    def calc_all_fitness(self, fitness_function):
        """
        Get all fitenss values in population

        @param {function} [fitness_function]: Fitness function to calculate fitness value
        """
        self.max_fitness = float('-inf')
        self.all_fitness_dict = {}

        for individual in self.individuals:
            chromosome = tuple(individual.chromosome)
            if chromosome in self.fitness_database:
                fitness = self.fitness_database[chromosome]

            else:
                fitness = fitness_function(individual)
                self.fitness_database[chromosome] = fitness    # Update database
                
            individual.fitness = fitness
            if fitness > self.max_fitness:
                    self.max_fitness = fitness

    def get_max_fitness(self):
        """
        Get the maximum fitness value in population

        @param {function} [fitness_function]: Fitness function to calculate fitness value
        @return {float}
        """
        return self.max_fitness
    
    def get_the_best_individual(self):
        """
        Get the individual with the best fitness

        @return {GA.components.Individaul} [the_best_indv]
        """

        max_value = self.get_max_fitness()
        the_best_indv = [individual for individual in self.individuals if individual.fitness == max_value]
        return the_best_indv[0]