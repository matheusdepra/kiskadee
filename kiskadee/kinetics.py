import pandas as pd
import numpy as np
import math
from scipy.constants import R
from scipy.stats import linregress
import matplotlib.pyplot as plt


class Kinetics():

    def __init__(self):

        self.fwo_result = {}
        self.kas_result = {}

    # Load sample data
    def loadData(self, data, heating_rates):
        self.data = data
        self.heating_rates = heating_rates
        self.logs_beta = [math.log(int(x)) for x in heating_rates]

    ##########################################################################################
    # Flynn-Wall-Ozawa (FWO) method
    ##########################################################################################

    # Create an array with correspondent alpha, 1/Temperature, Temperature and time
    # for further fwo calculation
    # May transform for KAS use
    def _fwo(self, alpha_min=0.1, alpha_max=0.8, alpha_spacing=0.1, alpha_array=None):
        # Accept an array with correspondent alpha sequence or calculate based on configuration
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
        # Iterate over alpha and heating rate range to build a matrix with necessary values
        for alpha in alpha_range:
            for hr in self.heating_rates:
                id = data[hr][data[hr]['alpha'] < alpha]['index'].idxmax()
                temperature = data[hr].iloc[id]['temperature_k']
                time = data[hr].iloc[id]['time']
                alpha_result.append( (alpha, 1/temperature, temperature, time) )
                
            result.append( alpha_result )
            alpha_result = []

        self.fwo_result = result
        return result, alpha_range

    # Main FWO calculation
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
                        "Temperature_Kelvin" : [],
                        "Temperature_Celsius" : [],
                        "Time" : [],
                        }


        for fwo in _fwo:
    
            _, inversetemp, temp, time = zip(*fwo)

            slope, intercept, r, p, se = linregress(inversetemp, self.logs_beta)

            dictResult["Slope"].append(slope)
            dictResult["R"].append(r)
            dictResult["Intercept"].append(intercept)
            dictResult["Poison"].append(p)
            dictResult["Std_Error"].append(se)
            # dictResult["Ea2"].append( (-slope/1000) * (R*1.052) ) #Transform from J/mol to kJ/mol
            dictResult["Ea"].append( (-slope * R / 1.052) / 1000 ) #Transform from J/mol to kJ/mol
            dictResult["R2"].append( r**2 )
            dictResult["Temperature_Kelvin"].append( temp[1] )
            dictResult["Temperature_Celsius"].append( temp[1] - 273.15 )
            dictResult["Time"].append( time[1] )

        # Transform result to dataframe
        dataframeResult = pd.DataFrame(dictResult)
        
        return dataframeResult

    # Plot FWO points and linear regression
    def plotFWO(
            self, 
            fwoData = None, 
            plt_xlabel = '1/T', 
            plt_ylabel = 'log (ß)', 
            plt_title = '',
            plt_legend_fontsize = 'x-large'
            ):

        if fwoData is None and self.fwo_result != {}:
            fwoData = self.fwo_result

            for res in fwoData:
                alpha, invtemp, _, _ = zip(*res)

                # Calculate linear regression points 
                slope, intercept, _, _, _ = linregress(invtemp, self.logs_beta) 
                regression = [intercept + slope*t for t in invtemp]

                plt.plot( invtemp, self.logs_beta, 'o', label='α= ' + str(alpha[0]))
                plt.plot( invtemp, regression, 'k--' )
            plt.xlabel(plt_xlabel)
            plt.ylabel(plt_ylabel)
            plt.title(plt_title)
            plt.legend( loc="upper right", bbox_to_anchor=(1.4, 1), shadow=False, fontsize=plt_legend_fontsize)

    ##########################################################################################
    # Kissinger-Akahira-Sunose (KAS) method
    ##########################################################################################
    
    def _kas(self, alpha_min=0.1, alpha_max=0.8, alpha_spacing=0.1, alpha_array=None):

        # Accept an array with correspondent alpha sequence or calculate based on configuration
        if alpha_array is None:
            # multiply 10 and divide to avoid floating point error
            alpha_range = np.arange(10*alpha_min, 10*(alpha_max+alpha_spacing), 10*alpha_spacing)/10
        else:
            alpha_range = alpha_array

        self.alpha_array = alpha_array

        data = self.data
        result = []
        alpha_result = []

        for alpha in alpha_range:
            for n, hr in enumerate(self.heating_rates):
                id = data[hr][data[hr]['alpha'] < alpha]['index'].idxmax()
                temperature = data[hr].iloc[id]['temperature_k']
                time = data[hr].iloc[id]['time']
                alpha_result.append( (alpha, math.log(hr/(temperature**2)) , 1000/temperature, time) )
                
            result.append( alpha_result )
            alpha_result = []


        self.kas_result = result
        return result, alpha_range


    # Main KAS calculation
    def KAS(self, alpha_min=0.1, alpha_max=0.8, alpha_spacing=0.1, alpha_array=None):
        
        _kas, _alpha_range = self._kas(
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
                        "Temperature_Kelvin" : [],
                        "Temperature_Celsius" : [],
                        "Time" : [],
                        }


        for kas in _kas:
    
            _, logtemp, temp, time = zip(*kas)
            slope, intercept, r, p, se = linregress(temp, logtemp)

            dictResult["Slope"].append(slope)
            dictResult["R"].append(r)
            dictResult["Intercept"].append(intercept)
            dictResult["Poison"].append(p)
            dictResult["Std_Error"].append(se)
            # dictResult["Ea2"].append( (-slope/1000) * (R*1.052) ) #Transform from J/mol to kJ/mol
            dictResult["Ea"].append( -slope*R ) #Transform from J/mol to kJ/mol
            dictResult["R2"].append( r**2 )
            dictResult["Temperature_Kelvin"].append( temp[1] )
            dictResult["Temperature_Celsius"].append( temp[1] - 273.15 )
            dictResult["Time"].append( time[1] )

        # Transform result to dataframe
        dataframeResult = pd.DataFrame(dictResult)
        
        return dataframeResult

    # Plot KAS points and linear regression
    def plotKAS(
            self, 
            kasData = None, 
            plt_xlabel = '1/T', 
            plt_ylabel = 'log (ß)', 
            plt_title = '',
            plt_legend_fontsize = 'x-large'
            ):

        if kasData is None and self.kas_result != {}:
            kasData = self.kas_result

            for res in kasData:
                alpha, logtemp, temp, time = zip(*res)

                # Calculate linear regression points 
                slope, intercept, _, _, _ = linregress(temp, logtemp) 
                regression = [intercept + slope*t for t in temp]

                plt.plot( temp, logtemp, 'o', label='α= ' + str(alpha[0]))
                plt.plot( temp, regression, 'k--' )

            plt.xlabel(plt_xlabel)
            plt.ylabel(plt_ylabel)
            plt.title(plt_title)
            plt.legend( loc="upper right", bbox_to_anchor=(1.4, 1), shadow=False, fontsize=plt_legend_fontsize)

