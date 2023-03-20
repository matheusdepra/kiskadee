import pandas as  pd

permittedExtensions = [
    'txt',
    'csv'
]

def checkExtensionFromPath(path):
    extension = path.split('.')[-1]

    return extension in permittedExtensions

class DataLoader():

    def __init__(self):
        self.data = {}
        self.sampleHeatingRates = {}
        self.sampleNames = []



    def read(self, name: str, heating_rate: int or float, path:str, sep: str='\t', col_names: list = ['time', 'temperature', 'mass']):

        # Check if file extension is valid        
        if not checkExtensionFromPath(path):
            raise ValueError(f'File extension not supported! Must be one of the following: {permittedExtensions}')


        data = pd.read_csv(path, sep=sep, names=col_names) 

        if name in self.data.keys():
            self.data[name][heating_rate] = data
            self.sampleHeatingRates[name].append(heating_rate)
        else:
            self.data[name] = { heating_rate : data}
            self.sampleNames.append(name)
            self.sampleHeatingRates[name] = [heating_rate]


        return f'{name} at {heating_rate} was loaded!'

    