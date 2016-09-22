import scipy
import scipy.fftpack
#from scipy.optimize import curve_fit
import pylab
from scipy import pi
import numpy
import glob
import re
from scipy.optimize import curve_fit

DO_PLOT = True

def func(x, a, c, d):
    return a*numpy.exp(-x*c)+d

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

#filelist = glob.glob('C:/data_resonator/fit/02182015/*.npy')
#filelist = glob.glob('C:/data_resonator/fit/03032015/*.npy')
#filelist = glob.glob('C:/data_resonator/fit/03062015/*.npy')
#filelist = glob.glob('C:/data_resonator/fit/07182015/*.npy')
#filelist = glob.glob('C:/data_resonator/fit/07232015/*.npy')
#filelist = glob.glob('C:/data_resonator/fit/08012015/*.npy')
#filelist = glob.glob('C:/data_resonator/fit/08032015/*.npy')
#filelist = glob.glob('C:/data_resonator/fit/08142015/*.npy')
filelist = glob.glob('C:/data_resonator/fit/20160729/*.npy')

intervall=200

for filename1 in filelist:
    print filename1
    list1 = find(filename1,'_')
    list2 = find(filename1,'.')
    freqstr = filename1[list1[len(list1)-2]+1:list2[0]]
    freqstr = freqstr.replace('_', '.')
    freq=float(freqstr)
    print freqstr
    data = numpy.load(filename1)
    triggerpos = numpy.nonzero(data[0:len(data),0]>0)[0][0]
    datav = data[triggerpos+4500:len(data)-000,:]
    meandata = numpy.mean(datav)
    datav=datav-meandata
    iterations = len(datav)/intervall
    newx = []
    newy = []
    newxm = []
    newym = []
    for k in range(1, iterations):
        if  len(newy)==0:
            newy.append(max(datav[intervall*(k-1):intervall*k,1]))
            cindex = numpy.where(datav[intervall*(k-1):intervall*(k),1]==max(datav[intervall*(k-1):intervall*(k),1]))
            newx.append(datav[cindex[0][0]+(k-1)*intervall,0])
        elif max(datav[intervall*(k-1):intervall*k,1])*0.8<newy[len(newy)-1]:
            newy.append(max(datav[intervall*(k-1):intervall*k,1]))
            cindex = numpy.where(datav[intervall*(k-1):intervall*(k),1]==max(datav[intervall*(k-1):intervall*(k),1]))
            newx.append(datav[cindex[0][0]+(k-1)*intervall,0])
        if  len(newym)==0:
            newym.append(min(datav[intervall*(k-1):intervall*k,1]))
            cindex = numpy.where(datav[intervall*(k-1):intervall*(k),1]==max(datav[intervall*(k-1):intervall*(k),1]))
            newxm.append(datav[cindex[0][0]+(k-1)*intervall,0])
        elif abs(min(datav[intervall*(k-1):intervall*k,1])*0.8)<abs(newy[len(newy)-1]):
            newym.append(min(datav[intervall*(k-1):intervall*k,1]))
            cindex = numpy.where(datav[intervall*(k-1):intervall*(k),1]==min(datav[intervall*(k-1):intervall*(k),1]))
            newxm.append(datav[cindex[0][0]+(k-1)*intervall,0])
    newx = numpy.array(newx)
    newy = numpy.array(newy)
    newxm = numpy.array(newxm)
    newym = numpy.array(newym)
    p01 = (-0.01, 6e+2,newym[len(newym)-2])
    p02 = (0.01, 6e+2,newy[len(newy)-2])
    popt1, pcov1 = curve_fit(func, newxm, newym,p01)
    popt2, pcov2 = curve_fit(func, newx, newy,p02)
    fitvaly1 = func(newxm, popt1[0],popt1[1],popt1[2])
    fitvaly2 = func(newx, popt2[0],popt2[1],popt2[2])
    print 1/popt1[1]
    print 1/popt2[1]
    print 1/popt1[1]*freq*1e6
    print 1/popt2[1]*freq*1e6
    print (1/popt1[1]*freq*1e6+1/popt2[1]*freq*1e6)/2
    x=datav[:,0]
    y=datav[:,1]
    if DO_PLOT:
        pylab.plot(x, y, 'bx')
        pylab.plot(newx, newy, 'go')
        pylab.plot(newxm, newym, 'go')
        pylab.plot(newxm, fitvaly1,'r-')
        pylab.plot(newx, fitvaly2,'r-')
        pylab.show()
