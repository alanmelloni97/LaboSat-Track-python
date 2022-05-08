import numpy as np
from matplotlib import pyplot as plt


tita=np.linspace(0,np.pi/2,100)
angulo=tita+np.pi
a=500
c=6400+a

b=a*np.cos(angulo)+(a**2*np.cos(angulo)**2-a**2+c**2)**0.5
D=b*np.cos(tita)
errory=D*np.sin(np.pi/180)

# plt.figure('D')
# plt.plot(tita*180/np.pi,D)

# plt.figure('Ey')
# plt.plot(tita*180/np.pi,errory)


anguloerr=np.arctan(errory/b)
plt.figure('anguloEY')
plt.plot(tita*180/np.pi,anguloerr*180/np.pi)
plt.title("Azimuth Error for diferent altitudes")
plt.xlabel("Alt")
plt.ylabel("Az Error")