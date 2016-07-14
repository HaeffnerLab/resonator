### Does NOT use the serialdevices infrastructure.
### Assumes COM1 port available for serial communication
### ('experimenter' machine only has one serial port)

### last update: B. Timar 2015-08-20


"""
### BEGIN NODE INFO
[info]
name = Pfeiffer Pressure Gauge
version = 1.0
description = 
instancename = Pfeiffer Pressure Gauge

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""


from serialconnection import PortFormat, SerialConnection
from labrad.server import LabradServer, Signal, setting
from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.errors import Error
from labrad.units import WithUnit

import serial

### port settings to access the Pfeiffer DualGauge which reads pressure
### inside the resonator apparatus

GaugeFormat = PortFormat(name ='COM1', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=5)




class GaugeServer( LabradServer ):
    """The Pfeiffer Gauge provides pressure values for the resonator experiment, connected to
the COM1 serial port on the windows machine"""

    name = 'Pfeiffer Pressure Gauge'

    #dictionary which tells you how many bytes you need to read for a given request after ENQ is sent.
    #includes CR, LF
    NUM_BYTES = { 'PR1':13+2, 'UNI':1+2}

    # number of bytes which are read after a request is sent, before replying with ENQ
    NUM_ACK_BYTES = 3

    #codes for units returned by the gauge
    UNIT_CODES = { 0: 'mbar', 1: 'torr', 2: 'Pa'}

    def initServer( self ):
      
        #first open the serial port
        try:
            self.connection = SerialConnection(GaugeFormat)
            print "Serial port opened successfully: {}".format(GaugeFormat.name)
    
        except serial.SerialException:
           
            raise Error("Failed to open port {}".format(GaugeFormat.name))

         

    def stopServer(self):
        
        if hasattr(self, 'connection'):
            print "Closing the serial port {}".format(GaugeFormat.name)
            self.connection.close()



    @setting(1, 'getPortname',  returns='s')
    def getPortname(self, c):
        """Name of the COM port being used"""
        return(GaugeFormat.name)

    @setting(2, 'getBaudrate', returns='i')
    def getBaudrate(self, c):
        """reutrn baud rate for the connection"""
        return GaugeFormat.baudrate

    @setting(3, 'getParity', returns= 's')
    def getParity(self, c):
        """ parity setting for the connection"""
        return GaugeFormat.parity

    @setting(4, 'getByteSize', returns ='i')
    def getByteSize(self, c):
        """number of data bits"""
        return GaugeFormat.bytesize

    @setting(5, 'getStopBits', returns='i')
    def getStopBits(self, c):
        """number of stop bits"""
        return GaugeFormat.stopbits

    @setting(6, 'getTimeout', returns='i')
    def getTimeout(self, c):
        """timeout, in seconds, for the serial connection"""
        return GaugeFormat.timeout

    @setting(11, 'WriteSerial', data= 's', returns = 'i')
    def writeSerial(self, c, data):
        """ Writes the given data to the serial port. Returns the number of bytes written"""
        nb = yield self._write(data)
        returnValue(nb)

    @setting(12, "ReadSerial", numbytes = 'i', returns='s')
    def readSerial(self, c, numbytes=10):
        """ Read specified number of bytes from the serial port ( if none provided, read 10)"""
        data = yield self._read(numbytes)
        returnValue(data)

    @setting(13, "ReadPressure", returns = ['v[mbar]', 'v[torr]', 'v[Pa]', 's'])
    def readPressure(self, c):
        """return the current pressure"""    
        pressure_str = yield self.getResponse('PR1')
        try:
            p = self.parsePressure(pressure_str)
        except Error as e:
           
            returnValue('Gauge off')
        else:
            units = yield self.getUnits(c)

            if (units == 'mbar'):
                #labrad doesn't recognize the mbar unit so switch to bar
                p = p/1000
                units = 'bar'
            
            returnValue(WithUnit(p, units))


        
    @setting(14, "getUnits", returns='s')
    def getUnits(self, c):
        """return the current pressure units"""
        respstr = yield self.getResponse('UNI')
        unitstr = self.UNIT_CODES[int(respstr)]
        returnValue(unitstr)


    @setting(21, "info", returns = 's')
    def info(self, c):
        info_str = """this is a Labrad server for the Pfeiffer Dual Gauge
                       which monitors pressure for the resonator experiment. 
                       Pressure values can be obtained by calling readpressure().
                       The Serial port settings can be viewed by clients but not edited.
                       They are determined by the pfeiffer specifications
                       you can edit the server file at 
                       C:\Users\experimenter\Desktop\LabRad\resonator\PfeifferGaugeServer.py 
                       on the windows machine. There is only one serial port on this machine, 
                       COM1, and it has to be open for the server to function."""
        return info_str
                       
    

                
    @inlineCallbacks
    def _write(self, data):
        """Write string to the port"""
        nb = yield self.connection.write(data)
        returnValue(nb)

    @inlineCallbacks
    def _writeCRLF(self, data):
        """Write string plus termination characters"""
        nb = yield self._write(data + '\r\n')
        returnValue(nb)
        
    @inlineCallbacks
    def _read(self, nb):
        """Read the specified number of bytes from the port"""
        data = yield self.connection.read(nb)
        returnValue(data)

  

    @inlineCallbacks
    def writeENQ(self):
        """Writes <ENQ> to the serial port to request transmission of previously specified data"""
        s = self.connection.getASCIICode('ENQ')
        yield self._writeCRLF(s)


    @inlineCallbacks
    def request(self, req):
        """ sends the specified 3-byte request string and returns whether or not the request
            was successfully acknowledged (1 if success)"""
        nb = yield self._writeCRLF(req)
        resp = yield self._read(self.NUM_ACK_BYTES)
        returnValue (not self.isError(resp))

    @inlineCallbacks
    def getResponse(self, req):
        """ submit the request specified by the 3-byte string REQ. if the request is acknowledged
        the response string will be returned, minus the CR LF. otherwise an error is raised"""
        ack = yield self.request(req)
        if (not ack):
            #raise Error('bad request to gauge')
            returnValue('bad request to gauge')
        else:
            
            nb_enq = yield self.writeENQ()
            resp = yield self._read(self.getNumBytes(req))
            if resp == '':
                returnValue('gauge off or not responding')
            else:
                resp = self.strip(resp)
                returnValue(resp)

    def strip(self,s):
        """remove termination characters from the end"""
        if ((s[-1] != '\n') or (s[-2] != '\r')):
            print "error here", s
            raise Error('bad string format')
        else:
            return s[:-2]
    
    def isError(self, s):
        """checks if output s from the gauge is an error"""
        if s == '':
            return False
        try:
            val= (self.strip(s) == self.connection.getASCIICode('NAK'))
        except Error:
            
            val = True
        
        return val
    def parsePressure(self, pstring):
        """ get the pressure value from the string returned by PR1"""
        try:
            start = pstring.index(', ') +2
            return float(pstring[start:])
        except ValueError:
            raise Error('Bad pressure string sent to parser')

    def getNumBytes(self, req):
        """ get the number of bytes that need to be read for the given request"""
        try:
            return self.NUM_BYTES[req]
        except KeyError:
            raise Error('bad request')

__server__= GaugeServer()

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)
