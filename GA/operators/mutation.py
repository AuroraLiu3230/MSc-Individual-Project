from ..components.individual import Individual
from random import random, uniform


class UniformMutation:
    """
    @param {float} [mutation_rate]: the probability of crossover (usually between 0.001 ~ 0.1)
    """
    def __init__(self, mutation_rate=0.01) -> None:

        if mutation_rate <= 0.0 or mutation_rate > 1.0:
            raise ValueError('Invalid crossover probability')
        self.mutation_rate = mutation_rate
    
    def mutate(self, individual):
        """
        Perform Uniform Mutation.

        @param {GA.components.Individual} [individual]
        @return {GA.components.Individual} : a mutated individual
        """

        do_mutate = random() < self.mutation_rate
        
        if do_mutate:
            
            for i, chromosome in enumerate(individual.chromosome):
                do_flip = random() < self.mutation_rate

                if not do_flip:
                    continue

                a, b = individual.ranges[i]
                n = round(uniform(a, b), individual.round)
                individual.chromosome[i] = n

        return individual

        

