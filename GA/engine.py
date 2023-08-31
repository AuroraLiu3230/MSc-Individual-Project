import pandas as pd
import json

class GA_Engine:
    """
    """
    def __init__(self, population, selection, crossover, mutation,
                 fitness_function=None, analysis=None, database_path=None) -> None:
        
        # Attributes assignment.
        self.population = population
        self.fitness_function = fitness_function
        self.selection = selection
        self.crossover = crossover
        self.mutation = mutation
        self.database_filepath = database_path
        self.chromo_keys = [f'chromo {idx+1}' for idx in range(len(population.individual_template.ranges))]
        self.max_fitness_dict = {key: [] for key in self.chromo_keys + ['Fitness']}


        self.population.calc_all_fitness(fitness_function)
        self._update_fitness_statistics()
        self.record_max(self.max_indv.chromosome, self.max_fitness)

    def record_max(self, chromosome, fitness):
        for key, value in zip(self.chromo_keys, chromosome):
            self.max_fitness_dict[key].append(value)
        self.max_fitness_dict['Fitness'].append(fitness)

    def run(self, n_generations=100):
        """
        @param {int} [n_generations]: the number of generations
        """

        # Check validity of fitness.
        if self.fitness_function is None:
            raise AttributeError('No fitness function in GA engine')

        local_size = self.population.size // 2
        # Start the evolution
        for generation in range(n_generations):
            self.current_generation = generation

            # Fill the new population
            local_individuals = []
            

            for _ in range(local_size):

                # Select parents:
                parent1, parent2 = self.selection.select(self.population, self.fitness_function)

                # Apply crossover
                child1, child2 = self.crossover.cross(parent1, parent2)

                # Apply mutation
                children = [self.mutation.mutate(child) for child in [child1, child2]]

                # Collect children
                local_individuals.extend(children)

            # Update the next generation
            self.population.initialize(local_individuals)
            self.population.calc_all_fitness(self.fitness_function)

            # Update the statistic variables
            self._update_fitness_statistics()

            # Record
            self.record_max(self.max_indv.chromosome, self.max_fitness)

            generation += 1
        
        self.to_dataframe()
            
    def _update_fitness_statistics(self):
        """
        Update the statistics related to fitness values in the GA engine.
        """
        # Update statistics for original fitness.
        self.max_indv = self.population.get_the_best_individual()
        self.max_fitness = self.max_indv.fitness

    def to_dataframe(self):
        self.max_df = pd.DataFrame(self.max_fitness_dict)

    def plot_fitness(self):
        self.max_df['Fitness'].plot()
