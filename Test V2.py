# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:36:23 2022

@author: alanm
"""

import orbit_prediction_V2 as op
import LabosaTrack_V2 as lst
import pandas as pd
import serial
import time
import numpy as np
import math
import sys

myLatLon=(-34.587353,-58.520116)
stepperFullRes=0.9
microstepping=16
stepperRes=stepperFullRes/microstepping
timeStep=1
magneticDeclination=0
a=0
orbit=pd.DataFrame()
satName=""
ALARM_OFFSET_SECONDS=60

try:
    serial_device=serial.Serial(port='COM8', baudrate=9600,stopbits=1,timeout=1,write_timeout=1)
except:
    print("ERROR: Couldn't connect to serial port")
    sys.exit("Error message")
    
sat=op.NextSatPass(myLatLon,10,45)
orbit,start=lst.SatTrack(myLatLon,sat.name,stepperFullRes,microstepping,timeStep)
lst.SendOrbit(serial_device,orbit,start,stepperRes,ALARM_OFFSET_SECONDS)