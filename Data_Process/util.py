import pandas as pd

class util:
    def transform_chromo_to_dict(chromosome):
        """
        Transform from chromosome type to dict type

        @param {list} [chromosome]
        @return {dict} 
        """
        parameter_dict = {}
        key = ['b1','b2','w1','w2','w3','w4','w5']

        for i in range(len(key)):
            parameter_dict[key[i]] = chromosome[i]
        return parameter_dict
    
    def transform_dict_to_chromo(parameter_dict):
        """
        Transform from dict type to chromosome type
        
        @param {dict} [parameter_dict]
        @return {list} [chromosome]
        """
        chromosome = []
        key = ['b1','b2','w1','w2','w3','w4','w5']

        for i in range(len(key)):
            chromosome.append(parameter_dict[key[i]])
        return chromosome
    
    def dataProcess(dName, file_path):
        column_names = ['Time', 'Bid', 'Ask', 'Volume']
        data = pd.read_csv(file_path, header=None, names=column_names, parse_dates=['Time'])
        data['Mid'] = (data['Ask']+data['Bid'])/2
        data['Time'] = pd.to_datetime(data['Time'], format="%Y%m%d %H%M%S%f")
        return data




    