class FitnessCalculator:
    def __init__(self, return_rate, mdd_rate):
        self.return_rate = return_rate
        self.mdd_rate = mdd_rate
    
    def calculate_fitness(self):
        fitness_value = self.return_rate - 0.1 * self.mdd_rate
    
        return round(fitness_value, 4)
