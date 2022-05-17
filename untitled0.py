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


def TxSerial(data,dataSize):
        Tx=str(data).encode()
        Tx+=bytes(dataSize-len(Tx))
        device.write(Tx)
        

device=serial.Serial(port='COM5', baudrate=115200,stopbits=1,timeout=2,write_timeout=1)

while True:
    Rx=device.read(1)
    print('recieved:',Rx)
    if Rx==b'\x01':
        TxSerial(time.time())
        TxSerial(time.time()+100)

 