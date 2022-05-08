import serial,math,time,pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
#%%
f401re=serial.Serial(port='COM5', baudrate=115200, stopbits=1,timeout=2,write_timeout=1)

#%%
start=pd.read_csv("csv/StepperStart.csv",index_col='Index')
start["Azimuth"][0]=math.trunc(start["Azimuth"][0]*1000)
start["Altitude"][0]=math.trunc(start["Altitude"][0]*1000)
start["AltDir Change"][0]=math.trunc(start["AltDir Change"][0]*1000)
start["Azimuth"]=start["Azimuth"].astype(int)
start["Altitude"]=start["Altitude"].astype(int)
start["AltDir Change"]=start["AltDir Change"].astype(int)

steps=pd.read_csv("csv/StepperSteps.csv",index_col='Index')
timepoints=(steps["Time"]*1000).astype(int)
steppoints=(steps["Steps"]).astype(int)

#%%
f401re.reset_input_buffer()
f401re.reset_output_buffer()
bufferSize=10

#%%
def TxSerial(data):
    Tx=str(data).encode()
    Tx+=bytes(bufferSize-len(Tx))
    f401re.write(Tx)
#%%
Rx=b'\x00'
while True:
    Rx=f401re.read(1)
    if Rx==b'\x01':
        
        # get current time with milliseconds=0
        a=time.time()
        while(time.time()<math.trunc(a)+1):
                True
        t=math.trunc(time.time())
        # send current time
        TxSerial(t)
        print(t)
        TxSerial('e')
        
        #Wait unit confirmation that RTC has been set
        Rx=f401re.read(1)
        if Rx==b'\x01':
            # send amount of points
            TxSerial(len(timepoints))
            TxSerial('a')
    
            TxSerial('1'*10)
            
            # send start data
            for i in range(len(start.columns)):
                TxSerial(start.iloc[0,i])
    
    
            # send timepoints
            for i in range(len(timepoints)):
                TxSerial(timepoints.iloc[i])
                
            TxSerial('2'*10)
            
            # send steppoints
            for i in range(len(steppoints)):
                TxSerial(steppoints.iloc[i])
                
            # send end communication message
            TxSerial('3'*10)
            TxSerial('b')
            Rx=b'\x00'
            f401re.reset_input_buffer()
            f401re.reset_output_buffer()
