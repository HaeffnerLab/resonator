"""Open a connection with specified settings"""
import serial

#
#
# last modified : 2015-08-06


class PortFormat(object):
    """Holds the details of the format of the serial connection: baud rate,
    number of bits, etc. """

    #default timeout values in seconds
    DEF_TIMEOUT = 10

    def __init__(self,name=0, baudrate = 9600, bytesize=8, parity='N', stopbits=1, timeout= DEF_TIMEOUT):

        self.name = name  
        #baud rate
        self.baudrate= baudrate    

        #number of data bits
        self.bytesize = bytesize

        #number of parity bits
        self.parity= parity

        #number of stop bits
        self.stopbits = stopbits

        #timeout in seconds
        self.timeout = timeout


class SerialConnection(serial.Serial):
    """Manages a single serial port, with one specific format"""

    ASCII_codes = {"ENQ": "\x05", "ACK":"\x06", "LF":"\x0A", "CR":"\x0D", "ETX":"\x03", "NAK":"\x15"}
    



    def __init__(self, portFormat=None):
        """ Open a connection at port <portName>. If no port name is provided,
            opens the first available port (as numbered by pyserial). If no data
            format is provided, use the default settings"""
        if (portFormat is None ):
            portName = 0
        else:
            portName = portFormat.name
        #opens the connection

        
        super(SerialConnection, self).__init__(port=portName)

        
        self.portFormat = portFormat
        
        if not (portFormat is None):
            #unpack the specified settings
            self.loadFormat(portFormat)

    def loadFormat(self, portFormat):
        """apply settings, if they are acceptable to serial.Serial"""
        self.setBaudrate(portFormat.baudrate)
        self.setByteSize(portFormat.bytesize)
        self.setParity(portFormat.parity)
        self.setStopbits(portFormat.stopbits)
        self.setTimeout(portFormat.timeout)


    def getASCIICode(self,msg):
        if not (msg in self.ASCII_codes.keys()):
            raise ValueError("not an allowed message")
        return self.ASCII_codes[msg]

  
