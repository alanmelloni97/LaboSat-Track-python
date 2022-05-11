import orbit_prediction as op
import time,datetime,math,pandas as pd,numpy as np
pd.options.mode.chained_assignment = None  # default='warn'
from tqdm import tqdm
from skyfield.api import load, wgs84

#%%
# https://celestrak.com/NORAD/elements/active.txt

start_time = time.time()
ts = load.timescale()
myLatLon=(-34.5873528,-58.5201163)
stepperFullRes=0.9
microstepping=16
stepperRes=stepperFullRes/microstepping
t = ts.now()
timeSteps=1

TLEs=op.DownloadTLEs()
satellite=op.SelectSat(TLEs,'STARLINK-3206')
print(satellite)
print("Time since epoch:",op.TimeSinceEpoch(satellite,t))
print()

t0 = ts.now()
taux=t0.utc_datetime()+datetime.timedelta(days=1)
t1 = ts.from_datetime(taux)
VisibleAltitude=10
op.CalculatePasses(satellite,myLatLon,t0,t1,VisibleAltitude)
bluffton = wgs84.latlon(myLatLon[0],myLatLon[1])
tx, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=VisibleAltitude)

#%%
# me aseguro que el primer timestamp sea el de rise
n=0
while events[n]!=0:
    n+=1
    
taux=tx.utc_datetime()
taux=taux[n+2]-taux[n]
orbitDf=op.PredictOrbit(satellite,myLatLon,tx[0],taux.seconds,timeSteps)

del orbitDf['Latitude']
del orbitDf['Longitude']
del orbitDf['Distance']
del orbitDf['Height']

orbitStart=math.trunc(orbitDf['Time'].iloc[0])
orbitDf['Time']-=orbitStart
orbitDf['dAlt'] = orbitDf['Altitude'] - orbitDf['Altitude'].shift(1)
orbitDf['dAz'] = orbitDf['Azimuth'] - orbitDf['Azimuth'].shift(1)
orbitDf['dAlt']=orbitDf['dAlt'].fillna(0)
orbitDf['dAz']=orbitDf['dAz'].fillna(0)
orbitDf['Steps']=0
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
        orbitDf['Steps'][ind]+=1

    altAngle+=abs(orbitDf['dAlt'][ind])
    if altAngle>=stepperRes:
        altStepCount+=1
        altAngle=altAngle-stepperRes
        orbitDf['Steps'][ind]+=2
   
    if orbitDf['dAlt'][ind]<0 and dirSetted==False:
        AltDirChange=orbitDf['Time'][ind]
        dirSetted=True
       
    if orbitDf['Steps'][ind]==0:
        orbitDf.drop([ind],axis=0,inplace=True)

#%%
startData={'Orbit Start':orbitStart,'Azimuth':orbitDf['Azimuth'].iloc[0],'Altitude':orbitDf['Altitude'].iloc[0],'AzDir':int(np.sign(orbitDf['dAz'].iloc[1])),'AltDir Change':AltDirChange}
startDf = pd.DataFrame(startData,index=[0])
startDf.index.name="Index"

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