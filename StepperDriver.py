import pandas as pd,serial,time,math
from datetime import datetime

def Average(lst):
    return sum(lst) / len(lst)

def GetCompassData():
    measures=[]  
    measure='.'
    while measure!='':    
        arduino.write(b'S')
        time.sleep(1)
        measure = arduino.readline().decode('utf-8')
        if measure!='':
            measures.append(measure)
    measures = [x.rstrip() for x in measures]   #remove '\r\n'
    measures= [i.split() for i in measures]     #separate words
    measuresX=[]
    measuresY=[]
    measuresZ=[]
    for i in measures:  #get axis values
        measuresX.append(int(i[1]))
        measuresY.append(int(i[3]))
        measuresZ.append(int(i[5]))
    measuresX=Average(measuresX)
    measuresY=Average(measuresY)
    measuresZ=Average(measuresZ)
    az= math.atan2(measuresX, measuresY) * 180 / math.pi;
    if az<0: 
        az=az+360
    return az


steps=pd.read_csv("csv/StepperSteps.csv",index_col='Index')
start=pd.read_csv("csv/StepperStart.csv",index_col='start')
arduino = serial.Serial(port='COM7', baudrate=115200, timeout=1, write_timeout=1)
### arduino resets when serial port is opened, so a delay is needed to wait for the arduino
print('Waiting for arduino start-up')
time.sleep(5)


stepperFullRes=0.9
microstepping=16
stepperRes=stepperFullRes/microstepping

### get azimuth start point
north=GetCompassData()                          #get magnetic north
magneticDeclination=-9.56                       #magnetic delclination from https://www.magnetic-declination.com/
trueNorth=north-magneticDeclination           
azimuthStart=start["Azimuth"][0]-trueNorth

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
startStepsAlt=start["Altitude"][0]/stepperRes

for step in range(0,abs(int(startStepsAz))):
    arduino.write(b'A')
    print("orienting Az",step)
    time.sleep(1/1000)

for step in range(0,int(startStepsAlt)):
    arduino.write(b'B')
    print("orienting Alt",step)
    time.sleep(1/1000)

#set azimuth direction
if start["AzDir"][0]==1:
    arduino.write(b'C') #spin clockwise
if start["AzDir"][0]==-1:
    arduino.write(b'D') #spin counterclockwise

time.sleep(1)

# wait until orbit timestamp to indicate steps
contAz,contAlt,i=0,0,0
changedDir=False
print("waiting step")
while i<=len(steps.index)-1:
    t=datetime.utcfromtimestamp(steps["Time"].iloc[i])  #get utc time from UNIX time
    while datetime.utcnow()<=t:
        True
    if steps['Step Az'].iloc[i]==1:
        arduino.write(b'A')
        contAz+=1
        print("Az",contAz)
    if steps['Step Alt'].iloc[i]==1:
        arduino.write(b'B')
        contAlt+=1
        print("Alt",contAlt)
    if changedDir==False and t>=datetime.utcfromtimestamp(start['AltDir Change'][0]):
        arduino.write(b'F')
        changedDir=True
        print("alt direction change",i)
    i+=1

print("pasada finalizada")
print("Az steps:",contAz)
print("Alt steps:",contAlt)

arduino.close()


