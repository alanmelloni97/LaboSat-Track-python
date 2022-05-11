import orbit_prediction as op
import LabosaTrack as lst
import pandas as pd


myLatLon=(-34.587353,-58.520116)
stepperRes=0.9
microstepping=16
timeStep=10
a=0
orbit=pd.DataFrame()
satName=""

print("Labosat-Track")
print("Current configuration:")
print("    Latitude:", myLatLon[0],"Longitude:",myLatLon[1])
print("    Time between orbit samples:", 1000/timeStep,"milliseconds")
print("    Steppers congiguration:")
print("        -Step resolution:",stepperRes)
print("        -Microstepping:",microstepping,end="\n\n")

def configure_system():
    
    print("Set Latitude:")
    myLat=int(input())
    while(myLat>90 or myLat<-90):
        print("Invalid entry, set latitude:")
        myLat=int(input())
        
    print("Set Longitude:")
    myLon=int(input())
    while(myLat>180 or myLat<-180):
        print("Invalid entry, set longitude")
        myLat=int(input())
    myLatLon=(myLat,myLon)
    
    print("Select time between samples:")
    print("1) 100 ms (algorithm time ~ 20 sec [testing only]")
    print("2) 10 ms  (algorithm time ~ 15 min [recommended]")
    print("3) 1 ms   (algorithm time ~ 40 min [only useful for orbits with altitude>80°]")
    timeStep=int(input())
    validValues={1,2,3,4}
    while(timeStep not in validValues):
        print("Invalid entry, select time between samples")
        timeStep=int(input())
    
    print("Select stepper's angle per step")
    print("1) 0.9°")
    print("2) 1.8°")
    stepperRes=int(input())
    validValues={1,2}
    while(stepperRes not in validValues):
        print("Invalid entry, enter 0 or 1")
        stepperRes=int(input())
        
    print("Select microstepping used")
    print("1) None")
    print("2) 2")
    print("3) 4")
    print("4) 8")
    print("5) 16")
    print("6) 32")
    print("7) 64")
    validValues={1,2,3,4,5,6,7}
    microstepping=int(input())
    while(microstepping not in validValues):
        print("Invalid entry, select microstepping used")
        microstepping=int(input())
    
    return myLatLon,timeStep,stepperRes,microstepping

while True:
        
    if orbit.empty:
        print("----No orbit selected----")
    else:
        print("----Orbit:",satName,"----")
        print("----Orbit start:",op.GetDatetimeFromUNIX(round(orbit["Time"].iloc[0],0)))
        print("----Max altitude:",max(orbit["Altitude"]))
        
    print("Select option:")
    print("1) Configure system")
    print("2) Select satellite by string")
    print("3) Select closest satellite")
    print("4) Start tracking through serial port")
    print("5) Send orbit data to microcontroller")
    print("0) Exit")
    
    a=input()
    
    if a=='0':
        break
    elif a=='1':
        myLatLon,timeStep,stepperRes,microstepping=configure_system()
        
    elif a=='2':   
        print("Paste satellite name from https://celestrak.com/NORAD/elements/active.txt")
        satName=int(input())
        orbit,start=lst.SatTrack(myLatLon,satName,stepperRes,microstepping,timeStep)
        
    elif a=='3':
        print("Selecting closest satellite...")
        sat=op.NextSatPass(myLatLon,10,50)
        print("Satellite selected:",sat)
        orbit,start=lst.SatTrack(myLatLon,sat.name,stepperRes,microstepping,timeStep)
        satName=sat.name
      
    elif a=='4':
        print("Connecting with Arduino...")
        lst.OnlineTracker(orbit,start,stepperRes,microstepping)
        
    elif a=='5':
        print("Sending orbit through serial port...")
        lst.OfflineTracking(orbit,start,stepperRes,microstepping)
            
    else:
        print("Incorrect input")
    
    print("")
        
