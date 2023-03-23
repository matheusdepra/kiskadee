import pandas as pd
import numpy as np

def _FWO( p_Alfas, p_Betas, p_ListDF ):
    l_Result = []
    
    l_AlfaResult = []
    for alfa in p_Alfas:
        for n, beta in enumerate( p_Betas ):
            l_Time = p_ListDF[n][p_ListDF[n]['alfa'] < alfa]["Time"].idxmax()
            l_Temp = p_ListDF[n].iloc[l_Time]["Temperature_K"]
            l_AlfaResult.append( (alfa, 1/l_Temp, l_Temp, l_Time) )
            
        l_Result.append( l_AlfaResult )
        l_AlfaResult = []

    return l_Result

class FWO():

    def __init__(self):

        self.fwo = {}

    def FWO(self, input, sample, alpha_min=0.1, alpha_max=0.8, alpha_space=0.1):
    
        alpha_range = np.arange(alpha_min, alpha_max+0.001, alpha_space)
        data = input.data[sample]
        heatingRate = input.sampleHeatingRates[sample]
        result = []
        alpha_result = []
        for alpha in alpha_range:
            for hr in heatingRate:
                id = data[hr][data[hr]['alpha'] < alpha]['index'].idxmax()
                temperature = data[hr].iloc[id]['temperature_k']
                time = data[hr].iloc[id]['time']
                alpha_result.append( (alpha, 1/temperature, temperature, time) )
                
            result.append( alpha_result )
            alpha_result = []

        return result

