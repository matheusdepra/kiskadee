import pandas as pd
import numpy as np
from scipy.stats import linregress
import math
from scipy.constants import R



class Kinetics():

    def __init__(self):

        self.fwo_result = {}

    def loadData(self, data, heating_rates):
        self.data = data
        self.heating_rates = heating_rates
        self.logs_beta = [math.log(int(x)) for x in heating_rates]

    def _fwo(self, alpha_min=0.1, alpha_max=0.8, alpha_spacing=0.1, alpha_array=None):
    
        if alpha_array is None:
            # multiply 10 and divide to avoid floating point error
            alpha_range = np.arange(10*alpha_min, 10*(alpha_max+alpha_spacing), 10*alpha_spacing)/10
        else:
            alpha_range = alpha_array

        self.alpha_array = alpha_array
        # data = tga.data[sample]
        # heatingRate = tga.sampleHeatingRates[sample]
        data = self.data
        result = []
        alpha_result = []
        for alpha in alpha_range:

            for hr in self.heating_rates:
                id = data[hr][data[hr]['alpha'] < alpha]['index'].idxmax()
                temperature = data[hr].iloc[id]['temperature_k']
                time = data[hr].iloc[id]['time']
                alpha_result.append( (alpha, 1/temperature, temperature, time) )
                
            result.append( alpha_result )
            alpha_result = []

        return result, alpha_range

    def FWO(self, alpha_min=0.1, alpha_max=0.8, alpha_spacing=0.1, alpha_array=None):
        
        _fwo, _alpha_range = self._fwo(
            alpha_min=alpha_min,
            alpha_max=alpha_max,
            alpha_spacing=alpha_spacing,
            alpha_array=alpha_array
            )
        
        dictResult = {  "alpha"      : _alpha_range, 
                        "Slope"     : [], 
                        "R"         : [], 
                        "R2"        : [], 
                        "Intercept" : [], 
                        "Poison"    : [], 
                        "Std_Error" : [],
                        "Ea"        : [],
                        "Ea2"        : [],
                        "Temperature_Kelvin" : [],
                        "Temperature_Celsius" : [],
                        "Time" : [],
                        }


        for fwo in _fwo:
    
            alpha, inversetemp, temp, time = zip(*fwo)

            slope, intercept, r, p, se = linregress(inversetemp, self.logs_beta)

            dictResult["Slope"].append(slope)
            dictResult["R"].append(r)
            dictResult["Intercept"].append(intercept)
            dictResult["Poison"].append(p)
            dictResult["Std_Error"].append(se)
            dictResult["Ea"].append( ( (-slope*R) / 0.457 ) / 1000 ) #Transform from J/mol to kJ/mol
            dictResult["Ea2"].append( (-slope/1000) * (R*1.052) ) #Transform from J/mol to kJ/mol
            dictResult["R2"].append( r**2 )
            dictResult["Temperature_Kelvin"].append( temp[1] )
            dictResult["Temperature_Celsius"].append( temp[1] - 273.15 )
            dictResult["Time"].append( time[1] )

  

        dataframeResult = pd.DataFrame(dictResult)

        
        return dataframeResult



