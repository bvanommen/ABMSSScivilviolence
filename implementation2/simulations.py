import Epstein_model as em
#import Epstein_dyna as dyna
import math
import matplotlib
import matplotlib.pyplot as plt

nstep = 100000

#dyna.model1(20,math.log(10),0.1,nstep,0.75,nstep,3,3,0.7,0.08)

nb_active1,nb_jail1 = em.model1(40,math.log(10),0.1,nstep,0.75,nstep/10,3,3,0.7,0.075,1)
nb_active2,nb_jail2 = em.model1(40,math.log(10),0.1,nstep,0.75,nstep/10,3,3,0.7,0.075,0)
#nb_active3,nb_jail3 = em.model1(40,math.log(10),0.1,10000,0.75,200,3,3,0.7,0.4)

time = list(range(nstep))

font = {'family' : 'normal', 'size' : 16}
matplotlib.rc('font', **font)
axis_font = {'fontname':'Arial', 'size':'17'}


#figures
plt.figure()
plt.plot(time, nb_active1, color='r', label='random cop motion')
plt.plot(time, nb_active2, color='b', label='clever cop motion')
plt.xlabel('steps',**axis_font)
plt.ylabel('number of active agents',**axis_font)
plt.legend(loc='lower right')
plt.show()

plt.figure()
plt.plot(time, nb_jail1, color='r', label='random cop motion') 
plt.plot(time, nb_jail2, color='b', label='clever cop motion')
plt.xlabel('steps',**axis_font)
plt.ylabel('number of imprisoned agents',**axis_font)
plt.legend(loc='lower right')
plt.show()
