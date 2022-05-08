import math as m
from matplotlib import pyplot as plt
import numpy as np
pi=m.pi
# h=1000
# ang1=0.015*math.pi/180
# ang2=0.03*math.pi/180
# area1=math.tan(ang1)*h
# area2=math.tan(ang2)*h
# areatot=math.sqrt(area1**2+area2**2)
# # print(areatot)

T=40*10**-9
G=3.2e-2


X=0.3
Y=0.3
dX=G
dY=G
derX=Y/(X**2+X*Y)
derY=1/(X+Y)
E=((dX*derX)**2+(dY*derY)**2)**0.5
ansInDeg=E*180/m.pi
print("G=",G)
print("Error [°]=",ansInDeg)



# angulos=np.linspace(20,90,1000)
# d=500/np.tan(angulos*pi/180)
# ancho=d*m.tan(1*pi/180)
# plt.plot(angulos,ancho)
# print("Error km:",ancho)
