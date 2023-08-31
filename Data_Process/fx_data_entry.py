from .util import util

class FX_data:
    def __init__(self, file_path, currency_pair, time) -> None:
        self.file_path = file_path
        self.currency_pair = currency_pair
        self.time = time
        self.data_name = currency_pair + " " + time
        self.data = util.dataProcess(dName=self.data_name, file_path=file_path)
        self.nTimeSteps = len(self.data)
        self.timelist = self.data['Time'].to_list()