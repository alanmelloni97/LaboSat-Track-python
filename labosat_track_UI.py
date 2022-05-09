import LabosaTrack as lst

orbit,start=lst.SatTrack((-30,-50),'STARLINK-1695',0.9,16,10,30)

a=0
print("Select option:")
print("1) Track Satellite")
print("2) Track closest satellite")
print("")
print("9) Set steppers resolution")

while True:
    if a==0:
        break
    if a==1:
        True
        
        