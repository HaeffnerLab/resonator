from pylab import *
a= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_27052015_1749_keithley_DMM.csv', delimiter=',')
b= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_25052015_1520_keithley_DMM.csv', delimiter=',')
c= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_28052015_1628_keithley_DMM.csv', delimiter=',')
e= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_30052015_1316_keithley_DMM.csv', delimiter=',')
f= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_30052015_1316_keithley_DMM.csv', delimiter=',')
#g1= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_03062015_1433_keithley_DMM.csv', delimiter=',')
#h= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_03062015_1433_keithley_DMM.csv', delimiter=',')
#i= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_04062015_1719_keithley_DMM.csv', delimiter=',')
g= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_09062015_1723_keithley_DMM.csv', delimiter=',')
h= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\C2_09062015_1723_keithley_DMM.csv', delimiter=',')
i= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_09062015_1723_keithley_DMM.csv', delimiter=',')
g1= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_12062015_1525_keithley_DMM.csv', delimiter=',')
h1= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\C2_12062015_1525_keithley_DMM.csv', delimiter=',')
i1= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_12062015_1525_keithley_DMM.csv', delimiter=',')

g2= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_12062015_1715_keithley_DMM.csv', delimiter=',')
h2= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\C2_12062015_1715_keithley_DMM.csv', delimiter=',')
i2= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_12062015_1715_keithley_DMM.csv', delimiter=',')

g3= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_22062015_1656_keithley_DMM.csv', delimiter=',')
h3= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\C2_22062015_1656_keithley_DMM.csv', delimiter=',')
i3= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_22062015_1656_keithley_DMM.csv', delimiter=',')

g4= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_22062015_2209_keithley_DMM.csv', delimiter=',')
h4= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\C2_22062015_2209_keithley_DMM.csv', delimiter=',')
i4= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_22062015_2209_keithley_DMM.csv', delimiter=',')

g5= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_23062015_1529_keithley_DMM.csv', delimiter=',')
h5= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\C2_23062015_1529_keithley_DMM.csv', delimiter=',')
i5= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_23062015_1529_keithley_DMM.csv', delimiter=',')

g6= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_24062015_1554_keithley_DMM.csv', delimiter=',')
h6= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\C2_24062015_1554_keithley_DMM.csv', delimiter=',')
i6= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_24062015_1554_keithley_DMM.csv', delimiter=',')

g7= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\526(Cold Finger)_06072015_1035_keithley_DMM.csv', delimiter=',')
h7= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\C2_06072015_1035_keithley_DMM.csv', delimiter=',')
i7= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\Cernox_06072015_1035_keithley_DMM.csv', delimiter=',')


d= loadtxt('Y:\\resonator-cooling\\Data\\resonator_auto\\cooldown_cryo_innsbruck_2009_1143_36.txt', delimiter='\t')
#plot(b[:,3],'b')
#plot(b[:,3],'r')
#plot(e[:,3],'m')
#plot(f[:,3],'green')
#plot(g[:,3],'c')
#plot(g[:,3],'c')
#plot(h[:,3],'k')
#plot(i[:,3],'k')

plot(g6[:,3],'r-x')
plot(h6[:,3],'g-x')
plot(i6[:,3],'b-x')

x1 = g1.shape[0] + 10 + arange(g2.shape[0])
plot(x1,g2[:,3],'r--')
plot(x1,h2[:,3],'g--')
plot(x1,i2[:,3],'b--')

x1 = arange(g3.shape[0]) - 177
plot(x1,g3[:,3],'c')
plot(x1,h3[:,3],'k')
plot(x1,i3[:,3],'y')

x1 = arange(g4.shape[0]) + g3.shape[0] -177
plot(x1,g4[:,3],'c')
plot(x1,h4[:,3],'k')
plot(x1,i4[:,3],'y')

x1 = arange(g7.shape[0]) + 20
plot(x1,g7[:,3],'r')
plot(x1,h7[:,3],'g')
#plot(x1,i7[:,3],'b')


#xc = arange(c.shape[0])+43
#plot(xc,c[:,3],'g')
#xd = d[:-2,0]/max(d[:-2,0])*180
#plot(xd,d[:-2,3],'y')
show()
