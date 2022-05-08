import orbit_prediction as op
import time
import datetime
from skyfield.api import load

# https://celestrak.com/NORAD/elements/active.txt

start_time = time.time()
ts = load.timescale()
myLat=-34.5873528
myLon=-58.5201163

t = ts.now()

TLEs=op.DownloadTLEs()
satellite=op.SelectSat(TLEs,'STARLINK-2609')
print(satellite)
print("Time since epoch:",op.TimeSinceEpoch(satellite,t))
print()

t0 = ts.now()
taux=t0.utc_datetime()+datetime.timedelta(days=1)
t1 = ts.from_datetime(taux)
VisibleAltitude=10
op.CalculatePasses(satellite,myLat,myLon,t0,t1,VisibleAltitude)

print("Data rigth now:")
print(op.GetCurrentTime())

lat,lon,hei=op.GetSatLatLongHei(satellite, t)
print('Latitude [°]:', lat.degrees)
print('Longitude [°]:', lon.degrees)
print('Height [km]:', hei)

alt,az,distance=op.GetSatAltAzDist(satellite, myLat, myLon, t)
print('Altitude [°]:', alt.degrees)
print('Azimuth [°]:', az.degrees)
print('Distance: {:.1f}'.format(distance.km))
print()

t=ts.utc(2022,2,18,1,39,53)
Period= 8460#in seconds
op.PredictOrbit(satellite,myLat,myLon,t,Period,100)


print("Algorithm time:")
print("--- %s seconds ---" % (time.time() - start_time))
