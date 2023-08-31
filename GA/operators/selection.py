from random import sample

class TournamentSelection:
    """
    Use Tournament Strategy with tournament size equals
    to two by default

    @param {int} [tournament_size]: the number of individuals in one tournament
    """
    def __init__(self, tournament_size) -> None:
        self.tournament_size = tournament_size

    def select(self, population, fitness_function):
        """
        @param {GA.components.Population} [population]: the population where the selection occurs
        @param {function} [fitness_function]: Fitness function to calculate fitness value

        @return {GA.components.Individual} [parent1, parent2]
        """

        def compete(competitors):
            """
            The competition function.

            @param {list of .Individuals} [competitors]
            @return {GA.components.Individual} [winner]
            """
            max_fitness = float('-inf')
            winner = None
            for individual in competitors:
                if individual.fitness > max_fitness:
                    winner = individual
                    max_fitness = individual.fitness

            return winner
        
        # Check validity of tournament size.
        if self.tournament_size >= population.size:
            raise ValueError('Tournament size ({}) is larger than population size ({})'.format(self.tournament_size, population.size))

        # Create lists of individuals for 2 tournaments
        tournament1 = sample(population.individuals, self.tournament_size)
        tournament2 = sample(population.individuals, self.tournament_size)

        # Pick winners of the two tournaments as parents
        parent1 = compete(tournament1)
        parent2 = compete(tournament2)

        return parent1, parent2

                
        


