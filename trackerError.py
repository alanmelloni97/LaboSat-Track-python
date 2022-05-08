import orbit_prediction as op

from skyfield.api import load
import pymap3d as pm
import math
import pandas as pd
import datetime

points=pd.read_csv("csv/gpsPoints.csv")
satellite=op.GetSatFromString(\
    "1 45017U 20003B   22040.46830159  .00009017  00000-0  29150-3 0  9993",\
    "2 45017  97.2346 105.1915 0014420  97.0564 321.0052 15.32203514115617",\
    "NUSAT-7 (SOPHIE)")
ts = load.timescale()
epoch=satellite.epoch.utc_datetime()


myLat= 27.7  
myLon=21.7


df = pd.DataFrame(columns=["LatError [Km]","LonError [Km]","HeiError [Km]","TotError [Km]","LatError [°]","LonError [°]","AzError [°]","AltError [°]","DistError [Km]","diff to epoch","Over Horizon"])
for index, row in points.iterrows():
    UNIXsec=points["t"][index]
    x=points["x"][index]
    y=points["y"][index]
    z=points["z"][index]

    timePoint=op.GetDatetimeFromUNIX(UNIXsec)
    t = ts.from_datetime(timePoint)
    lat,lon,hei=op.GetSatLatLongHei(satellite, t)
    latGps,lonGps,heiGps=pm.ecef2geodetic(x, y, z, deg=True)
    
    alt,az,dist=op.GetSatAltAzDist(satellite,myLat,myLon,t)
    azGps,altGps,distGps=pm.ecef2aer(x, y, z, myLat,myLon,0,deg=True)
    
    latError=abs(lat.degrees-latGps)
    lonError=abs(lon.degrees-lonGps)
    latErrorKm=op.GetDistanceTwoCoords(lat.degrees,0,latGps,0)
    lonErrorKm=op.GetDistanceTwoCoords(0,lon.degrees,0 ,lonGps)
    heiError=abs(hei-heiGps/1000)
    totalError=math.sqrt(latErrorKm**2+lonErrorKm**2+heiError**2)
    azError=abs(az.degrees-azGps)
    altError=abs(alt.degrees-altGps)
    distError=abs(dist.km-distGps/1000)
    diffEpoch=timePoint-epoch
    
    azErrorRad=azError*math.pi/180
    altErrorRad=altError*math.pi/180
    azErrorKm=math.tan(azErrorRad)*dist.km
    altErrorKm=math.tan(altErrorRad)*dist.km
    FOVRadius=math.sqrt(azErrorKm**2+altErrorKm**2)
    
    if alt.degrees<0:
        OverHorizon=False
    else:
        OverHorizon=True  
    
    
    df2=pd.DataFrame( \
        [[latErrorKm,lonErrorKm,heiError,totalError,latError,lonError,azError,altError,distError,diffEpoch,OverHorizon]], \
        index=[timePoint], \
        columns=["LatError [Km]","LonError [Km]","HeiError [Km]","TotError [Km]","LatError [°]","LonError [°]","AzError [°]","AltError [°]","DistError [Km]","diff to epoch","Over Horizon"])
    df=df.append(df2)
df.to_csv("csv/OrbitError "+satellite.name+datetime.datetime.now().strftime(' %Y-%m-%d_%H-%M.csv')+".csv")
print(satellite)
print(df)
