# -*- coding: utf-8 -*-


"""
### BEGIN NODE INFO
[info]
name = MSOX Server
version = 1.0
description = Server for Agilent MSOX 3024A

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.server import setting
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue
import numpy
from numpy import * 

class MSOXWrapper(GPIBDeviceWrapper):

    @inlineCallbacks
    def setdatasourcestr(self, channel): #sets source for all queries to channel if channel dependend
        result = yield self.write(':WAVeform:SOURce CHANnel' + str(channel))
        returnValue(result)

    @inlineCallbacks
    def singleStr(self):
        result = yield self.write(':SINGle')
        returnValue(result)

    @inlineCallbacks
    def IdenStr(self):
        result = yield self.query('*IDN?')
        returnValue(result)

    @inlineCallbacks
    def getX0str(self): #gets trigger time
        result = yield self.query(':WAVeform:XORigin?')
        returnValue(result)

    @inlineCallbacks
    def getXincstr(self): #gets time step
        result = yield self.query(':WAVeform:XINCrement?')
        returnValue(result)

    @inlineCallbacks
    def getYmultistr(self):
        result = yield self.query(':WAVeform:YINCrement?')
        returnValue(result)

    @inlineCallbacks
    def getYoffstr(self):
        result = yield self.query(':WAVeform:YREFerence?')
        returnValue(result)

    @inlineCallbacks
    def getY0str(self): #get Y0
        result = yield self.query(':WAVeform:YORigin?')
        returnValue(result)

    @inlineCallbacks
    def getDatastr(self): #gets current displayed waveform data
        result = yield self.query(':WAVeform:DATA?')
        returnValue(result)

    @inlineCallbacks
    def getPointsstr(self): #gets current amount of transfered points
        result = yield self.query(':WAVeform:POINts?')
        returnValue(result)

    @inlineCallbacks
    def setPointsstr(self, points): #sets number of transmitted points {100 | 250 | 500 | 1000 | 2000 | 5000 | 10000 | 20000| 50000 | 100000 | 200000 | 500000 | 1000000 | 2000000| 4000000 | 8000000 | <points mode>}
        result = yield self.write(':WAVeform:POINts ' + str(points))
        returnValue(result)

    @inlineCallbacks
    def getFormatstr(self): #gets current data resolution
        result = yield self.query(':WAVeform:FORMat?')
        returnValue(result)

    @inlineCallbacks
    def setFormatstr(self, resolution): #sets data resolution {WORD | BYTE | ASCii}
        result = yield self.write(':WAVeform:FORMat ' + resolution)
        returnValue(result)                    

class MSOxServer(GPIBManagedServer):
    #Provides basic control for Agilent MSO-X 3024A Oscilloscope
    name = 'MSOX Server'
    deviceName = 'AGILENT TECHNOLOGIES MSO-X 3024A'#,MY54100486,02.36.2013091301'
    deviceWrapper = MSOXWrapper

    # def createDict(self):
    #     d = {}
    #     d['X0'] = None #trigger position
    #     d['Xinc'] = None #time increment
    #     d['Ymulti'] = None #Voltage increment
    #     d['Yoff'] = None #Voltage offset
    #     d['Y0'] = None # position of 0V
    #     d['Datalength'] = None #number of datapoints
    #     d['readystate'] = None # boolean 1=ready to trigger, 0= triggered, waiting for next command
    #     self.tdsDict = d
    #
    # @inlineCallbacks
    # def populateDict(self, c):
    #     X0 = yield self._readX0(c)
    #     Xinc = yield self._readXinc(c)
    #     Ymulti = yield self._readYmulti(c)
    #     Yoff = yield self._readYoff(c)
    #     Y0 = yield self._readY0(c)
    #     Datalength = yield self._readdatalength(c)
    #     Datasource = yield self._readdatasource(c)
    #
    #     self.createDict()
    #
    #     self.tdsDict['X0'] = float(X0)
    #     self.tdsDict['Xinc'] = float(Xinc)
    #     self.tdsDict['Ymulti'] = float(Ymulti)
    #     self.tdsDict['Yoff'] = float(Yoff)
    #     self.tdsDict['Y0'] = float(Y0)
    #     self.tdsDict['Datalength'] = int(Datalength)
    #     self.tdsDict['Datasource'] = Datasource

    @setting(101, 'Identify', returns='s')
    def Identify(self, c):
        '''Ask current instrument to identify itself'''
        dev = self.selectedDevice(c)
        answer = yield dev.IdenStr()
        returnValue(answer)


    @setting(102, 'readYref', returns='v')
    def readYref(self,c):
        dev = self.selectedDevice(c)
        answer = yield self._readYoff(c)
        returnValue(answer)
       
       
    @setting(103, 'setchannel',channelnbr='i' , returns='')
    def setchannel(self,c,channelnbr):
        '''Set the Channel you want to take data from'''
        dev = self.selectedDevice(c)
        answer = yield dev.setdatasourcestr(channelnbr)
        returnValue(answer)
       
       
    @setting(104, 'getcurve', returns='*2v')  # ??? why *2v ?
    def getcurve(self, c):
        yield self.populateDict(c)
        dev = self.selectedDevice(c)
        dev.encASCIIstr()
        datastr = yield self._readData(c)
        datastr = datastr[10:len(data)]
        dataarray = numpy.fromstring(datastr, sep=' ')
        voltarray =(dataarray-self.tdsDict['Yoff'])*self.tdsDict['Ymulti']+self.tdsDict['Y0']
        t0=self.tdsDict['X0']
        dt=self.tdsDict['Xinc']
        length=self.tdsDict['Datalength']        
        tarray = t0 + dt*array(range(length))        
        intarr = numpy.vstack((tarray,voltarray))
        answer = intarr.transpose()
        returnValue(answer)

    @setting(105, 'getvalue', returns='v')
    def getvalue(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getvaluestr()
        returnValue(answer)

    @setting(106, 'checkunits', returns='s')
    def checkunits(self,c):
        dev = self.selectedDevice(c)
        answer = yield dev.checkunitstr()
        returnValue(answer)
        
    @setting(107, 'setpk2pk', returns='')
    def setpk2pk(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.setpk2pkstr()
        print 'success'
        returnValue(answer)
        
    @setting(108, 'setpoints',points='i' , returns='')
    #valid input {100 | 250 | 500 | 1000 | 2000 | 5000 | 10000 | 20000| 50000 | 100000 | 200000 | 500000 | 1000000 | 2000000| 4000000 | 8000000 | <points mode>}
    def setpoints(self, c, points):
        dev = self.selectedDevice(c)
        answer = yield dev.setPointsstr(points)
        returnValue(answer)

    @setting(109, 'setformat',resolution='s', returns='')
    #valid input {WORD | BYTE | ASCii}
    def setformat(self, c, resolution):
        dev = self.selectedDevice(c)
        answer = yield dev.setFormatstr(resolution)
        returnValue(answer)


    @setting(110, 'getraw', returns='s')
    #gets raw data from oscilloscope
    def getraw(self, c):
        dev = self.selectedDevice(c)
        datastr = yield self._readData(c)
        datastr = datastr[10:len(datastr)]
        dataarray = numpy.fromstring(datastr, sep=' ')
        answer = datastr
        returnValue(answer)

    @setting(111, 'gettimestr', returns='*v')
    #gets the time str for
    def gettimestr(self,c):
        dev = self.selectedDevice(c)
        t0 = yield self._readX0(c)
        dt = yield self._readXinc(c)
        length = yield dev.getPointsstr()
        testa=range(int(length))
        tarray = [float(t0) + float(dt)*t for t in testa]
        returnValue(tarray)

    @setting(112, 'getpoints', returns='i')
    #valid input {100 | 250 | 500 | 1000 | 2000 | 5000 | 10000 | 20000| 50000 | 100000 | 200000 | 500000 | 1000000 | 2000000| 4000000 | 8000000 | <points mode>}
    def getpoints(self, c, points):
        dev = self.selectedDevice(c)
        answer = yield dev.getPointsstr()
        answer = int(answer)
        returnValue(answer)

    @setting(113, 'getformat', returns='s')
    #valid input {WORD | BYTE | ASCii}
    def getformat(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getFormatstr()
        returnValue(answer)

    @setting(114, 'getYmulti', returns='v')
    #valid input {WORD | BYTE | ASCii}
    def getYmulti(self, c):
        dev = self.selectedDevice(c)
        answer = yield self._readYmulti(c)
        returnValue(answer)

    @setting(115, 'getYorigin', returns='v')
    #valid input {WORD | BYTE | ASCii}
    def getYorigin(self, c):
        dev = self.selectedDevice(c)
        answer = yield self._readY0(c)
        returnValue(answer)

    @setting(116, 'singletrig', returns='')
    #valid input {WORD | BYTE | ASCii}
    def singletrig(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.singleStr()
        returnValue(answer)

    @inlineCallbacks
    def _readX0(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getX0str()
        returnValue(answer)        

    @inlineCallbacks
    def _readXinc(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getXincstr()
        returnValue(answer)        
        
    @inlineCallbacks
    def _readYmulti(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getYmultistr()
        returnValue(answer)        
        
    @inlineCallbacks
    def _readYoff(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getYoffstr()
        returnValue(answer)        

    @inlineCallbacks
    def _readdatasource(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getdatassourcestr()        
        returnValue(answer)

    @inlineCallbacks
    def _readY0(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getY0str()
        returnValue(answer)

    @inlineCallbacks
    def _readdatalength(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.getdatalengthstr()        
        returnValue(answer)
        
    @inlineCallbacks
    def _readready(self, c):
        dev = self.selectedDevice(c)
        answer = yield dev.setreadystr()        
        returnValue(answer) 

    @inlineCallbacks
    def _readData(self, c):
       dev = self.selectedDevice(c)
       answer = yield dev.getDatastr()        
       returnValue(answer)

__server__ = MSOxServer()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
