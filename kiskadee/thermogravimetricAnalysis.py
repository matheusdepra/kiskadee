from dataLoader import DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, filtfilt

def massLoss(mass):
    result = []

    for i in mass:
        massLoss = 1 - ( ( mass[0] - i ) / ( mass[0] - mass.iloc[-1] ) )
        result.append(massLoss*100)
    

    return result

def celsius2kelvin(temperature):
    return temperature + 273.15

def alphaConversion(mass):
    
    result = []
    
    for i in mass:
        alpha = ( ( mass[0] - i ) / ( mass[0] - mass.iloc[-1] ) )
        result.append(alpha)
        
    
    return result


# TODO => Check diff with time and notice the differences between
# Notice that np.gradient() is in use, because is recomended to not
# equaly spaced data
def dtg( mass_loss, temperature ):
        
    return np.gradient(mass_loss) / np.gradient(temperature)

#Retira ruidos
def savgolSmooth(data, window:  int, order: int):

    return savgol_filter(data, window, order)


filterSwitch = {
    'savgol' : savgolSmooth
}


class TGA(DataLoader):

    def __init__(self):
        super().__init__()
        pass

    def massLossAndConversions(self):

        if self.data == {}:
            raise ValueError('No data available! Please define the data to be used with .read() function!')
            
        # Iterate over key and values
        for key, value in self.data.items():
            for k, v in value.items():
                # set mass loss
                _massLoss = massLoss(v['mass'])
                self.data[key][k]['mass_loss'] = _massLoss
                
                # convert celsius to kelvin
                self.data[key][k]['temperature_k'] = celsius2kelvin(v['temperature'])

                # alpha conversion
                _alpha = alphaConversion(v['mass'])
                self.data[key][k]['alpha'] = _alpha

    # TODO => implement an ALL alterative
    def plotTGA(self, sample: str):

        # Check if provided sample name is valid!
        if sample not in self.sampleNames:
            raise ValueError(f'{sample} sample not found! Please use a valid sample name')

        # Get sample
        data = self.data.get(sample, None)

        if data is None: raise ValueError(f'{sample} sample not found! Please use a valid sample name')

        for k, v in data.items():
            plt.plot( v["temperature"], v["mass_loss"], label=f'{k} °C/min')

        # Plot labels and legends
        plt.xlabel("Temperature (°C)")
        plt.ylabel("Mass Loss (%)")
        plt.legend( loc="upper right", bbox_to_anchor=(0.98, 0.98), shadow=False, fontsize='large')
        plt.title( f'TGA - {sample}' )

    # TODO => implement an ALL alterative
    def dtg(self, sample: str):

        if self.data == {} or sample not in self.sampleNames:
            raise ValueError('No data available! Please define the data to be used with .read() function!')

        for k, v in self.data[sample].items():
            _mass_loss = v['mass_loss']
            _temperature = v['temperature']

            self.data[sample][k]['dtg'] = dtg(_mass_loss, _temperature)

    def dtgFull(self):
        for sample in self.sampleNames:
            self.dtg(sample)

    # TODO => implement an ALL alterative
    def plotDTG(self, sample: str, smoothed: bool = False):

        # Check if provided sample name is valid!
        if sample not in self.sampleNames:
            raise ValueError(f'{sample} sample not found! Please use a valid sample name')

        columnName = 'dtg_smoothed' if smoothed else 'dtg'

        # Get sample
        data = self.data.get(sample, None)

        if data is None: raise ValueError(f'{sample} sample not found! Please use a valid sample name')

        for k, v in data.items():
            plt.plot( v["temperature"], v[columnName], label=f'{k} °C/min')

        # Plot labels and legends
        plt.xlabel("Temperature (°C)")
        plt.ylabel("DTG")
        plt.legend( loc="upper right", bbox_to_anchor=(0.98, 0.98), shadow=False, fontsize='large')
        plt.title( f'DTG - {sample}' )

    def plotDTGFull(self, smoothed: bool = False):
        for sample in self.sampleNames:
            self.plotDTG(sample, smoothed)

    def removeData(self, index_to_drop, sample:str, heating_rate: int or float):

        self.data[sample][heating_rate].drop(index=index_to_drop, axis=0, inplace=True)
        self.data[sample][heating_rate].reset_index(inplace=True)

        
    def smoothData(
            self, sample: str, 
            heating_rate: int or float, 
            window: int = 20,
            order: int = 2,
            column: str = 'dtg',
            filter: str = 'savgol'
            ):
       
        filterFunc = filterSwitch[filter]

        newColumnName = f'{column}_smoothed'
        data = self.data[sample][heating_rate][column]

        if filter == 'savgol':
            self.data[sample][heating_rate][newColumnName] = filterFunc(data, window, order)
        else:
            raise ValueError('Select a valid filter!')
        
    def smoothDataFull(self,            
            window: int = 20,
            order: int = 2,
            column: str = 'dtg',
            filter: str = 'savgol'):
        
        for sample in self.sampleNames:
            for hr in self.sampleHeatingRates[sample]:
                self.smoothData(sample, hr, window, order, column, filter)
   
    def plotAlpha(self, sample: str):

        # Check if provided sample name is valid!
        if sample not in self.sampleNames:
            raise ValueError(f'{sample} sample not found! Please use a valid sample name')

        # Get sample
        data = self.data.get(sample, None)

        if data is None: raise ValueError(f'{sample} sample not found! Please use a valid sample name')

        for k, v in data.items():
            plt.plot( v["temperature"], v["alpha"], label=f'{k} °C/min')

        # Plot labels and legends
        plt.xlabel("Temperature (°C)")
        plt.ylabel("Conversion (α)")
        plt.legend( loc="upper right", bbox_to_anchor=(0.98, 0.40), shadow=False, fontsize='large')
        plt.title( f'Alpha Conversion - {sample}' )
