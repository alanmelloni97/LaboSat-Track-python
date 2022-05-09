from skyfield.api import load, wgs84
from skyfield.api import EarthSatellite
import datetime
import pandas as pd
from tqdm import tqdm
import geopy.distance

def DownloadTLEs():
    #Download TLEs from all active satellites from celestrack.com
    #Returns: dictionary with names and TLEs
    print("Downloading all active TLEs:")
    stations_url = 'https://celestrak.com/NORAD/elements/active.txt'
    satellites = load.tle_file(stations_url,reload=True)
    print('Loaded', len(satellites), 'satellites')
    print()
    return {sat.name: sat for sat in satellites}

def GetSatFromString(line1,line2,name):
    ts = load.timescale()
    return EarthSatellite(line1, line2, name, ts)

def SelectSat(TLEList,satName):
    #Selects one satellite from a TLE dictionary
    #Parameters: Dictionary of satellites and satellite name
    #returns: satellite object
    satellite = TLEList[satName]
    return satellite

def TimeSinceEpoch(sat,t):
    # t must be a Time object
    epoch=sat.epoch.utc_datetime()
    t=t.utc_datetime()
    return epoch-t

def CalculatePasses(sat,myLatLon,fromT,toT,visibleAltitude):
    #Prints when will a satellite be visible
    #Takes a satellite object, latitud and longitude, date to start calculating, last date to be calculated and altitude angle considered to be visible
    bluffton = wgs84.latlon(myLatLon[0], myLatLon[1])
    t, events = sat.find_events(bluffton, fromT, toT, altitude_degrees=visibleAltitude)
    for ti, event in zip(t, events):
        name = ('rise above '+str(visibleAltitude)+'°', 'culminate', 'set below '+str(visibleAltitude)+'°')[event]
        print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)
    print()
        
def GetCurrentTime():
    ts = load.timescale()
    return ts.now().utc_jpl()
        
def GetSatLatLongHei(sat,t):
    geocentric = sat.at(t)
    lat, lon = wgs84.latlon_of(geocentric)
    hei = wgs84.height_of(geocentric).km
    return lat,lon,hei
    
def GetSatAltAzDist(sat,myLatLon,t):
    bluffton = wgs84.latlon(myLatLon[0], myLatLon[1])
    difference = sat - bluffton
    topocentric = difference.at(t)
    alt, az, distance = topocentric.altaz()
    return alt,az,distance

def PredictOrbit(sat,myLatLon,startTime,PeriodInSeconds,timeUnit):
    print("calculating orbit...")
    df = pd.DataFrame(columns=["Time","Latitude","Longitude","Height","Altitude","Azimuth","Distance"])

    for i in tqdm(range(0,PeriodInSeconds*timeUnit)):
        IterationTime = startTime+datetime.timedelta(milliseconds=i*(1000/timeUnit))
        lat,lon,hei= GetSatLatLongHei(sat, IterationTime)
        alt,az,distance= GetSatAltAzDist(sat, myLatLon, IterationTime)
        df2=pd.DataFrame( \
            [[round(IterationTime.utc_datetime().timestamp(),3),lat.degrees,lon.degrees,hei,alt.degrees,az.degrees,distance.km]], \
            index=[i], \
            columns=["Time","Latitude","Longitude","Height","Altitude","Azimuth","Distance"])
        df=pd.concat([df,df2])
    df.to_csv("csv/trackedOrbit.csv")
    return df
    
def IsSatInSunligth(sat,t):
    eph = load('de421.bsp')
    sunlit = sat.at(t).is_sunlit(eph)
    return sunlit

def GetDistanceTwoCoords(lat1,lon1,lat2,lon2):
    return geopy.distance.distance((lat1,lon1),(lat2,lon2)).km

def GetDatetimeFromUNIX(seconds):
    return datetime.datetime.fromtimestamp(seconds,datetime.timezone.utc)

# def NextPass()

def NextSatPasses(myLatLon,tStartOffset,tEndOffset,visibleAltitude):
    ts = load.timescale()
    t0 = ts.from_datetime(ts.now().utc_datetime()+datetime.timedelta(minutes=tStartOffset))
    t1 = ts.from_datetime(t0.utc_datetime()+datetime.timedelta(minutes=tEndOffset))
    TLEs=DownloadTLEs()
    bluffton = wgs84.latlon(myLatLon[0],myLatLon[1])
    for key in TLEs.keys():
        satellite=SelectSat(TLEs,key)
        t, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=visibleAltitude)
        for ti, event in zip(t, events):
            print(satellite)
            name = ('rise above '+str(visibleAltitude)+'°', 'culminate', 'set below '+str(visibleAltitude)+'°')[event]
            print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)
    
    