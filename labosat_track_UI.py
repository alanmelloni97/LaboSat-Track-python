import orbit_prediction as op
import LabosaTrack as lst

# orbit,start=lst.SatTrack((-30,-50),'STARLINK-1695',0.9,16,10,30)

myLatLon=(-34.587353,-58.520116)
stepperRes=0.9
microstepping=16
timeStep=10
a=0

while True:
    print("Select option:")
    print("1) Set your coordinates")
    print("2) Select satellite by string")
    print("3) Select closest satellite")
    print("4) Start tracking through serial port")
    print("5) Send orbit data to microcontroller")
    print("8) Configure prediction parameters")
    print("9) Configure steppers")
    print("0) Exit")
    
    a=input()
    
    if a=='0':
        break
    elif a=='1':
        print("Set Latitude:")
        myLatLon[0]=input()
        print("Set Longitude:")
        myLatLon[1]=input()
    elif a=='2':   
        print("Paste satellite name from https://celestrak.com/NORAD/elements/active.txt")
        satName=input()
        orbit,start=lst.SatTrack(myLatLon,satName,stepperRes,microstepping,timeStep)
    elif a=='3':
        print("Selecting closest satellite...")
        sat=op.NextSatPass((-30,-50),10,50)
        print("Satellite selected:",sat)
        orbit,start=lst.SatTrack(myLatLon,sat.name,stepperRes,microstepping,timeStep)
      
    elif a=='4':
        print("Connecting with Arduino...")
        print("Orbit start:",orbit[""])
        lst.OnlineTracker(orbit,start,stepperRes,microstepping)
        
        
    elif a=='8':
        print("select time between samples:")
        print("1) 100 ms (algorithm time ~ 20 sec [testing only]")
        print("2) 10 ms  (algorithm time ~ 10 min [recommended]")
        print("3) 1 ms   (algorithm time ~ ? s [only useful for orbits with altitude>80°]")
        
    else:
        print("Incorrect input")
    
    print("")
        
        
        