import orbit_prediction as op
import time
import datetime
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from tqdm import tqdm
from skyfield.api import load, wgs84

#%%
# https://celestrak.com/NORAD/elements/active.txt

start_time = time.time()
ts = load.timescale()
myLat=-34.5873528
myLon=-58.5201163
stepperFullRes=0.9
microstepping=16
stepperRes=stepperFullRes/microstepping
t = ts.now()
timeSteps=10
unixOffset=1640995200

TLEs=op.DownloadTLEs()
satellite=op.SelectSat(TLEs,'MONOLITH')
print(satellite)
print("Time since epoch:",op.TimeSinceEpoch(satellite,t),end='\n\n')

t0 = ts.now()
taux=t0.utc_datetime()+datetime.timedelta(days=1)
t1 = ts.from_datetime(taux)
VisibleAltitude=10
op.CalculatePasses(satellite,myLat,myLon,t0,t1,VisibleAltitude)
bluffton = wgs84.latlon(myLat, myLon)
tx, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=VisibleAltitude)

#%%
# me aseguro que el primer timestamp sea el de rise
n=0
while events[n]!=0:
    n+=1
    
taux=tx.utc_datetime()
taux=taux[n+2]-taux[n]
orbitDf=op.PredictOrbit(satellite,myLat,myLon,tx[n],taux.seconds,timeSteps)

del orbitDf['Latitude']
del orbitDf['Longitude']
del orbitDf['Distance']
del orbitDf['Height']

# orbitDf['Time']-=unixOffset
# orbitDf['Time']*=1000
orbitDf['dAlt'] = orbitDf['Altitude'] - orbitDf['Altitude'].shift(1)
orbitDf['dAz'] = orbitDf['Azimuth'] - orbitDf['Azimuth'].shift(1)
orbitDf['dAlt']=orbitDf['dAlt'].fillna(0)
orbitDf['dAz']=orbitDf['dAz'].fillna(0)
orbitDf['Step Alt']=0
orbitDf['Step Az']=0
orbitDf.index.name="Index"

#%%
dirSetted= False
azStepCount,azAngle,altStepCount,altAngle=0,0,0,0
for ind in tqdm(orbitDf.index):
    
    if abs(orbitDf['dAz'][ind])>300:
        if(orbitDf['dAz'][ind])>0:
            orbitDf['dAz'][ind]-=360
        if(orbitDf['dAz'][ind])<0:
            orbitDf['dAz'][ind]+=360
        
    azAngle+=abs(orbitDf['dAz'][ind])
    if azAngle>=stepperRes:
        azStepCount+=1
        azAngle=azAngle-stepperRes
        orbitDf['Step Az'][ind]=1

    altAngle+=abs(orbitDf['dAlt'][ind])
    if altAngle>=stepperRes:
        altStepCount+=1
        altAngle=altAngle-stepperRes
        orbitDf['Step Alt'][ind]=1
   
    if orbitDf['dAlt'][ind]<0 and dirSetted==False:
        AltDirChange=orbitDf['Time'][ind]
        dirSetted=True
       
    if orbitDf['Step Alt'][ind]==0 and orbitDf['Step Az'][ind]==0:
        orbitDf.drop([ind],axis=0,inplace=True)

#%%
startData={'Azimuth':orbitDf['Azimuth'].iloc[0],'Altitude':orbitDf['Altitude'].iloc[0],'AzDir':int(np.sign(orbitDf['dAz'].iloc[0])),'AltDir Change':AltDirChange}
startDf = pd.DataFrame(startData,index=[0])
startDf.index.name="start"

#%%
print()
print("Start Azimuth:",startDf['Azimuth'][0])
print("Start Altitude:",startDf['Altitude'][0])
print("Azimuth direction",startDf['AzDir'][0])
print("Maximum Altitude",orbitDf['Altitude'].max())
print("Maximum dAlt",abs(orbitDf['dAlt']).max())
print("Maximum dAz",abs(orbitDf['dAz']).max())
print("Alt steps:",altStepCount)
print("Az steps:",azStepCount)

# del orbitDf['Altitude']
# del orbitDf['Azimuth']
# del orbitDf['dAlt']
# del orbitDf['dAz']

orbitDf=orbitDf.loc[~(orbitDf==0).all(axis=1)]
orbitDf.to_csv("csv/StepperSteps.csv")
startDf.to_csv("csv/StepperStart.csv")

print()
print("Algorithm time:")
print("--- %s seconds ---" % (time.time() - start_time))