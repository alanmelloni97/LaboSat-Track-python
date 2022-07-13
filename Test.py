# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:36:23 2022

@author: alanm
"""

import orbit_prediction as op
import LabosaTrack as lst
import pandas as pd
import serial
import time
import numpy as np
import math

myLatLon=(-34.587353,-58.520116)
stepperFullRes=0.9
microstepping=16
stepperRes=stepperFullRes/microstepping
timeStep=5
magneticDeclination=0
a=0
orbit=pd.DataFrame()
satName=""

sat=op.NextSatPass(myLatLon,10,45)
orbit,start=lst.SatTrack(myLatLon,"ISS (ZARYA)",stepperFullRes,microstepping,timeStep)
lst.OfflineTracking(orbit,start,stepperRes)
