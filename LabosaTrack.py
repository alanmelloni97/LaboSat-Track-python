import orbit_prediction as op
from skyfield.api import load, wgs84
import time
import datetime
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'
from tqdm import tqdm
import serial
import math
    
def Orbit2steps(orbitDf,stepperRes):
    
    del orbitDf['Latitude']
    del orbitDf['Longitude']
    del orbitDf['Distance']
    del orbitDf['Height']
    orbitDf['dAlt'] = (orbitDf['Altitude'] - orbitDf['Altitude'].shift(1)).fillna(0)
    orbitDf['dAz'] = (orbitDf['Azimuth'] - orbitDf['Azimuth'].shift(1)).fillna(0)
    orbitDf['Steps']=0
    orbitDf.index.name="Index"
    
    dirSetted= False
    azStepCount,azAngle,altStepCount,altAngle=0,0,0,0
    for ind in tqdm(orbitDf.index):
        
        if abs(orbitDf['dAz'][ind])>300:
            if(orbitDf['dAz'][ind])>0:
                orbitDf['dAz'][ind]-=360
            if(orbitDf['dAz'][ind])<0:
                orbitDf['dAz'][ind]+=360
            
        azAngle+=abs(orbitDf['dAz'][ind])
        while azAngle>=stepperRes:
            azStepCount+=1
            azAngle=azAngle-stepperRes
            orbitDf['Steps'][ind]+=1
    
        altAngle+=abs(orbitDf['dAlt'][ind])
        while altAngle>=stepperRes:
            altStepCount+=1
            altAngle=altAngle-stepperRes
            orbitDf['Steps'][ind]+=100
       
        if orbitDf['dAlt'][ind]<0 and dirSetted==False:
            AltDirChange=orbitDf['Time'][ind]
            dirSetted=True
           
        if orbitDf['Steps'][ind]==0:
            orbitDf.drop([ind],axis=0,inplace=True)
    
    azimuthStart=orbitDf['Azimuth'].iloc[0]
    if azimuthStart>180:
        azimuthStart-=360
    if azimuthStart<-180:
        azimuthStart+=360
                
    startData={'AzDir':int(np.sign(orbitDf['dAz'].iloc[0])),'Azimuth':azimuthStart,'Altitude':orbitDf['Altitude'].iloc[0],'AltDir Change':AltDirChange,'Stepper Res':stepperRes}
    startDf = pd.DataFrame(startData,index=[0])
    startDf.index.name="start"
    return orbitDf,startDf
    
def PrintOrbitDf(orbitDf,startDf,azStepCount,altStepCount):
    print("Start Azimuth:",startDf['Azimuth'][0])
    print("Start Altitude:",startDf['Altitude'][0])
    print("Azimuth direction",startDf['AzDir'][0])
    print("Maximum Altitude",orbitDf['Altitude'].max())
    print("Maximum dAlt",abs(orbitDf['dAlt']).max())
    print("Maximum dAz",abs(orbitDf['dAz']).max())
    print("Alt steps:",altStepCount)
    print("Az steps:",azStepCount)

def SatTrack(myLatLon,satName,stepperFullRes,microstepping,timeStep):
    stepperRes=stepperFullRes/microstepping
    
    start_time = time.time()
    ts = load.timescale()

    TLEs=op.DownloadTLEs()
    satellite=op.SelectSat(TLEs,satName)
    print("Time since epoch:",op.TimeSinceEpoch(satellite,ts.now()),flush=True)
    print(satName)
    
    t0 = ts.now()
    t1 = ts.from_datetime(t0.utc_datetime()+datetime.timedelta(days=1))
    bluffton = wgs84.latlon(myLatLon[0], myLatLon[1])
    tx, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=0)
    
    #%%
    # me aseguro que el primer timestamp sea el de rise
    n=0
    while events[n]!=0:
        n+=1
    taux=tx.utc_datetime()
    taux=taux[n+2]-taux[n]
    orbitDf=op.PredictOrbit(satellite,myLatLon,tx[n],taux.seconds,timeStep)
    orbitDf,startDf=Orbit2steps(orbitDf,stepperRes)
    
    #%%
    
    # del orbitDf['Altitude']
    # del orbitDf['Azimuth']
    # del orbitDf['dAlt']
    # del orbitDf['dAz']
    
    # orbitDf=orbitDf.loc[~(orbitDf==0).all(axis=1)]
    orbitDf.to_csv("csv/StepperSteps.csv")
    startDf.to_csv("csv/StepperStart.csv")
    
    print()
    print("Algorithm time:")
    print("--- %s seconds ---" % (time.time() - start_time))
    return orbitDf,startDf

#%%
def OnlineTracker(stepsDf,startDf,stepperRes,magneticDeclination):

    try:
        arduino = serial.Serial(port='COM5', baudrate=115200, timeout=1, write_timeout=1)
    except:
        print("ERROR: Couldn't connect to serial port")
        return
    
    
    print('Waiting for arduino start-up...')
    time.sleep(5)

    ## get azimuth start point
    # north=GetCompassData(arduino)                   #get magnetic north
    # print("megnetometer:",north,'°')
    # magneticDeclination=-9.56                       #magnetic delclination from https://www.magnetic-declination.com/
    # trueNorth=north-magneticDeclination           
    # # azimuthStart=startDf["Azimuth"][0]-trueNorth
    azimuthStart=startDf["Azimuth"][0]+magneticDeclination
    print('Azimuth:',azimuthStart,'°',flush=True)
    
    
    if azimuthStart>180:
        azimuthStart-=360
    if azimuthStart<-180:
        azimuthStart+=360
        
    # orient motors to initial angles
    if azimuthStart>=0:
        arduino.write(b'C')
    if azimuthStart<0:
        arduino.write(b'D')
        
    startStepsAz=azimuthStart/stepperRes
    startStepsAlt=startDf["Altitude"][0]/stepperRes
    
    print('orienting Azimuth:',flush=True)
    for step in tqdm(range(0,abs(int(startStepsAz)))):
        arduino.write(b'A')
        time.sleep(1/1000)
    
    print()
    print('orienting Altitude:',flush=True)
    for step in tqdm(range(0,int(startStepsAlt))):
        arduino.write(b'B')
        time.sleep(1/1000)
        
    #set azimuth direction
    if startDf["AzDir"][0]==1:
        arduino.write(b'C') #spin clockwise
    if startDf["AzDir"][0]==-1:
        arduino.write(b'D') #spin counterclockwise

    contAz,contAlt,i=0,0,0
    changedDir=False
    print("waiting step...")
    while i<=len(stepsDf.index)-1:
        t=datetime.datetime.utcfromtimestamp(stepsDf["Time"].iloc[i])  #get utc time from UNIX time
        while datetime.datetime.utcnow()<=t:
            True
        while stepsDf['Steps'].iloc[i] % 100 >= 1:
            arduino.write(b'A')
            stepsDf['Steps'].iloc[i]-=1
            contAz+=1
            
        while stepsDf['Steps'].iloc[i] >= 100:
            arduino.write(b'B')
            stepsDf['Steps'].iloc[i]-=100
            contAlt+=1
            print("Alt",contAlt,end='\r')
        if changedDir==False and t>=datetime.datetime.utcfromtimestamp(startDf['AltDir Change'][0]):
            arduino.write(b'F')
            changedDir=True
            print("alt direction change",i)
        print("Az:",contAz,"Alt:",contAlt,end='\r\r')
        i+=1
    
    print("pasada finalizada")
    print("Az steps:",contAz)
    print("Alt steps:",contAlt)
    
    arduino.close()
#%%
def OfflineTracking(stepsDf,startDf,stepperRes):
   
    print(op.GetDatetimeFromUNIX(stepsDf['Time'].iloc[0]))
    
    try:
        f401re=serial.Serial(port='COM8', baudrate=9600,stopbits=1,timeout=1,write_timeout=1)
    except:
        print("ERROR: Couldn't connect to serial port")
        return

    orbitStart=math.trunc(stepsDf['Time'].iloc[0])
    stepsDf['Time']-=orbitStart
    startDf['AltDir Change']-=orbitStart

    startDf["Azimuth"][0]=math.trunc(startDf["Azimuth"][0]*1000)
    startDf["Altitude"][0]=math.trunc(startDf["Altitude"][0]*1000)
    startDf["AltDir Change"][0]=math.trunc(startDf["AltDir Change"][0]*1000)
    startDf["Stepper Res"][0]=math.trunc(startDf["Stepper Res"][0]*1000)
    startDf["Azimuth"]=startDf["Azimuth"].astype(int)
    startDf["Altitude"]=startDf["Altitude"].astype(int)
    startDf["AltDir Change"]=startDf["AltDir Change"].astype(int)
    startDf["Stepper Res"]=startDf["Stepper Res"].astype(int)
    
    timepoints=(stepsDf["Time"]*1000).astype(int)
    steppoints=stepsDf["Steps"].astype(int)
    
    data=startDf["Altitude"].to_list()+startDf['AltDir Change'].to_list()+ startDf["Stepper Res"].to_list()+timepoints.to_list()+steppoints.to_list()
    f401re.reset_input_buffer()
    print(startDf)
    #%%
    def TxSerial(Txdata):
        f401re.write(Txdata.to_bytes(4,"big"))
        
    def TxSerial_atoi(Txdata,dataSize):
        Tx=str(Txdata).encode()
        Tx+=bytes(dataSize-len(Tx))
        f401re.write(Tx)
    #%%
    n=0
    cont=0
    f401re.write(b'p')

    while True:
        while f401re.read(1)!=b'\x01':
            True
        if n==0:
            now=time.time()
            while(time.time() < math.trunc(now)+1):
                True
            t=math.trunc(time.time())
            TxSerial(t)
            print(t)
        elif n==1:
            t=int(time.time())+60
            TxSerial(t)
            print(t)
        elif n==2:
            TxSerial(len(timepoints))
        elif n==3:   
           TxSerial_atoi(startDf["AzDir"].iloc[0],4)
           TxSerial_atoi(startDf["Azimuth"].iloc[0],7)
        elif n==4:
            for i in data:
                cont+=1
                if(cont!=0 and cont % 1000 == 0):
                    print(cont)
                    while f401re.read(1)!=b'\x01':
                        True        
                TxSerial(i)
                i+=1
            break
        n+=1
    
    
    
    
    
    
    
   
#%%     

# def GetCompassData(serialDevice):
    
#     def Average(lst):
#         return sum(lst) / len(lst)
    
#     measures=[]  
#     measure='.'
#     while measure!='':    
#         serialDevice.write(b'S')
#         time.sleep(1)
#         measure = serialDevice.readline().decode('utf-8')
#         if measure!='':
#             measures.append(measure)
#     measures = [x.rstrip() for x in measures]   #remove '\r\n'
#     measures= [i.split() for i in measures]     #separate words
#     measuresX=[]
#     measuresY=[]
#     measuresZ=[]
#     for i in measures:  #get axis values
#         measuresX.append(int(i[1]))
#         measuresY.append(int(i[3]))
#         measuresZ.append(int(i[5]))
#     measuresX=Average(measuresX)
#     measuresY=Average(measuresY)
#     measuresZ=Average(measuresZ)
#     az= math.atan2(measuresX, measuresY) * 180 / math.pi;
#     if az<0: 
#         az=az+360
#     return az
        
