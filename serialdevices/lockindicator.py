 
from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from labrad.server import Signal
import numpy

class lockindicator( SerialDeviceServer ):
    """Controls lockindicator box in laser room"""

    name = 'laserlockservre'
    regKey = 'laserlock'
    port = None
    serNode = 'cctmain'
    timeout = 1.0

    @inlineCallbacks
    def initServer( self ):
        self.createDict()
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise
        yield self.populateDict()

    def createDict(self):
        d = {}
        d['0'] = 0 #laser 0
        d['1'] = 0 #laser 1
        d['2'] = 0 #laser 2
        d['3'] = 0 #laser 3
        d['4'] = 0 #laser 4
        d['5'] = 0 # 422
        d['6'] = 0 #laser 6
        d['7'] = 0 #laser 7        
        self.tpsDict = d

    @setting(1, "status", channel='i', returns='b')
    def status(self, c, channel):
        '''returns status of channel'''

        returnValue(answer)
