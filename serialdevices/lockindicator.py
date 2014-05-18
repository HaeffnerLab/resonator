 
from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from labrad.server import Signal
import numpy
import binascii

class lockindicator( SerialDeviceServer ):
    """Controls lockindicator box in laser room"""

    name = 'laserlockserver'
    regKey = 'laserlock'
    port = None
    serNode = 'cctmain'
    timeout = 1.0

    laserupdate = Signal(611088, 'signal: laserlock', 'i')

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


    @inlineCallbacks
    def getstatus(self):
        yield self.ser.write_line('d')
        answer=yield self.ser.readline()
        intans=int(binascii.hexlify(answer),16)
        self.notifyOtherListeners(c, intans, self.laserupdate)


    def notifyOtherListeners(self, context, message, f):
        """
        Notifies all listeners except the one in the given context, executing function f
        """
        notified = self.listeners.copy()
        notified.remove(context.ID)
        f(message,notified)

if __name__ == "__main__":
    from labrad import util
    util.runServer(laserlockserver())


