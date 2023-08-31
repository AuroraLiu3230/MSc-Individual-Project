from random import random
from copy import deepcopy

class UniformCrossover:
    """
    @param {float} [crossover_rate]: the probability of crossover
    @param {float} [gene_exchange_rate]: the probability of gene exchange
    """
    def __init__(self, crossover_rate, gene_exchange_rate) -> None:
        
        if crossover_rate <= 0.0 or crossover_rate > 1.0:
            raise ValueError('Invalid crossover probability')
        self.crossover_rate = crossover_rate

        if gene_exchange_rate <= 0.0 or gene_exchange_rate > 1.0:
            raise ValueError('Invalid gene exchange probability')
        self.gene_exchange_rate = gene_exchange_rate

    def cross(self, parent1, parent2):
        """
        Perform uniform crossover by crossing the chromosomes of the parents.

        @param {GA.components.Individual} [parent1, parent2]
        @return {GA.components.Individual} [child1, child2]
        """

        do_cross = random() < self.crossover_rate

        if not do_cross:
            child1, child2 = deepcopy(parent1), deepcopy(parent2)
        
        else:
            # Chromosome for 2 children
            chromosome1 = deepcopy(parent1.chromosome)
            chromosome2 = deepcopy(parent2.chromosome)

            for i, (gene1, gene2) in enumerate(zip(chromosome1, chromosome2)):
                do_exchange = random() < self.gene_exchange_rate
                if do_exchange:
                    chromosome1[i], chromosome2[i] = gene2, gene1

            child1, child2 = parent1.clone(), parent2.clone()
            child1.initialize(chromosome=chromosome1)
            child2.initialize(chromosome=chromosome2)

        return child1, child2