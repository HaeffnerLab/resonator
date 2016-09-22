import scipy
import scipy.fftpack
import pylab
from scipy import pi
import numpy
import glob
import re
import time

def get_peaks(filelist, peaks, peaks2, peaks3):
    try:
        for filename1 in filelist:
            start_t = time.time()
            filename1 = filename1.replace('\\','/')
            print filename1
            data = numpy.load(filename1)
    #        print "load: " + str(time.time()-start_t)
            #triggerpos = numpy.nonzero(data[0:len(data),0]>0)[0][0]
            #print triggerpos
            triggerpos = len(data)-2**14
    #        print len(data)
            datav = data[triggerpos:len(data),:]
    #        print "fft start: " + str(time.time()-start_t)
            #FFT=abs(scipy.fft(datav[0:len(datav),1]))
            FFT=abs(scipy.fft(datav[:,1]))
    #        print FFT.shape
    #        print "fft: " + str(time.time()-start_t)
            freqs = scipy.fftpack.fftfreq(len(datav),datav[1,0]-datav[0,0])
            ffta= [freqs,FFT]
            ffta = numpy.transpose(ffta)

            nullpos = numpy.nonzero(ffta[0:len(data),0]<0)[0][0]

            cleanfft = ffta[0:nullpos-1,:]
            inde= FFT.argsort()[-4:][::-1]
    #        print filename1
            start = [m.start() for m in re.finditer('/', filename1)][-1]
            freq= filename1[start+1:len(filename1)-8]
    #        print freq

            freq = freq.replace('/','')
            if freq.rfind('.')!=freq.find('.'):
                freq=freq[0:freq.rfind('.')-1]
            ffreq = float(freq)*1e6
            print ffreq/1e6
            if ffreq < 1e9:
                indexf= numpy.nonzero(ffta[0:len(datav),0]>ffreq)[0][0] #finds index for current measurement frequency
                indexf2= numpy.nonzero(ffta[0:len(datav),0]>2 * ffreq)[0][0] #finds index for current measurement frequency
                indexf3= numpy.nonzero(ffta[0:len(datav),0]>3 * ffreq)[0][0] #finds index for current measurement frequency
                #print indexf2
                #print indexf
                avgfft = numpy.mean(cleanfft[indexf-1:indexf+1,1])
                avgfft2 = numpy.mean(cleanfft[indexf2-1:indexf2+1,1])
                avgfft3 = numpy.mean(cleanfft[indexf3-1:indexf3+1,1])

                #print avgfft
                #print avgfft2
                peaks= numpy.append(peaks, [cleanfft[indexf,0],ffreq,avgfft])
                peaks2= numpy.append(peaks2, [cleanfft[indexf2,0],ffreq,avgfft2])
                peaks3= numpy.append(peaks3, [cleanfft[indexf3,0],ffreq,avgfft3])
                #print peaks
                #print peaks2
        #        print "finish: " + str(time.time()-start_t)
    except SyntaxError:
        pass


    peaks = numpy.reshape(peaks, (len(peaks)/3,3))
    peaks2 = numpy.reshape(peaks2, (len(peaks2)/3,3))
    peaks3 = numpy.reshape(peaks3, (len(peaks3)/3,3))
    return peaks, peaks2, peaks3

peaks = numpy.array([])
peaks2 = numpy.array([])
peaks3 = numpy.array([])
done_list = []
try:
    while(True):
        filelist = glob.glob('c:/data_resonator/data_auto/*.npy')
        to_do = [val for val in filelist if not val in done_list]
        peaks, peaks2, peaks3  = get_peaks(to_do, peaks, peaks2, peaks3)
        done_list = done_list + to_do
        print "Close plot window to search for new data"

        pylab.plot(peaks2[:,1], peaks2[:,2], 'rx', label='2nd')
        pylab.plot(peaks3[:,1], peaks3[:,2], 'ks', label = '3rd')
        pylab.plot(peaks[:,1], peaks[:,2], 'go-', label='fund')
        pylab.legend()
        pylab.show()
        #time.sleep(10)
except KeyboardInterrupt:
    pass


pylab.plot(peaks[:,1], peaks[:,2], 'go')
##pylab.subplot(211)
##pylab.plot(datav[:,0], datav[:,1])
##pylab.subplot(212)
##pylab.plot(cleanfft[:,0],20*scipy.log10(cleanfft[:,1]),'x')
pylab.show()
numpy.savetxt('peaksresults20160729.txt',peaks)
