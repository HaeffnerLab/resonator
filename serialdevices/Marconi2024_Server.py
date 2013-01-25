# Serial version
# Requires serial_server_v1_2.py to be running in labrad
# Simply inherits from serialdeviceserver

#"""
#### BEGIN NODE INFO
#[info]
#name = Marconi Server
#version = 1.0
#instancename = Marconi Server
#
#[startup]
#cmdline = %PYTHON% %FILE%
#timeout = 20
#
#[shutdown]
#message = 987654321
#timeout = 5
#### END NODE INFO
#"""

from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks,\
                                    SerialDeviceError, SerialConnectionError
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from labrad.server import Signal
#from labrad.types import Error


# DEBUGGING TOOL
def ann(method):
    def wrapped(*args):
        print "Starting", method
        return method(*args)
    return wrapped


SIGNALID = 209057
SIGNALID1 = 209058

class MarconiServer(SerialDeviceServer):
    """Server for basic CW control of Marconi RF Generator"""
    
    name = 'Marconi Server'
    regKey = 'MarconiKey' 
    # set MarconiKey in registry to ttyUSB# (# is USB port connection)
    port = None
    serNode = 'resonatormain' # labradnode
    timeout = 1.0
    gpibaddr = 11

    onNewUpdate = Signal(SIGNALID, 'signal: settings updated', '(sv)')
    onStateUpdate = Signal(SIGNALID1, 'signal: state updated', 'b')  
    
    @inlineCallbacks
    def initServer(self):
        self.createDict()
        if not self.regKey or not self.serNode: 
            raise SerialDeviceError('Must define regKey and serNode attributes')
        port = yield self.getPortFromReg(self.regKey)
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

        #self.SetControllerMode(1) # prologix set to controller mode, not necessary
        yield self.ser.write(self.SetAddrStr(self.gpibaddr)) # set gpib address
        self.SetControllerWait(0)   # turn off auto listen after talk, 
                                    # to stop line unterminated errors
        self.SetEOIState(1)         # enable EOI assertion at last written character
                                    # frees the device to respond to the query
        yield self.populateDict()
        if True:
            print(self.marDict)
        self.listeners = set()

    def createDict(self):
        d = {}
        d['state'] = None # state is boolean
        d['freq'] = None # frequency in MHz
        d['power'] = None # power in dBm
        d['power_units'] = None # power (will be) in dBm
        d['power_range'] = None
        d['freq_range'] = None
        self.marDict = d
    
    @inlineCallbacks
    def populateDict(self):
        state = yield self._GetState() 
        freq = yield self._GetFreq()
        power = yield self._GetPower()
        State = self.parseState(state)
        self.marDict['state'] = bool(State) 
        self.marDict['power'] = float(power)
        self.marDict['freq'] = float(freq)
        self.marDict['power_units'] = 'DBM' # default
        self.marDict['power_range'] = [-100, 13]
        self.marDict['freq_range'] = [0, 1000]
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
        
    def getOtherListeners(self,c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified
    

    # ===== SETTINGS (available to user) ======

    @setting(1, "Identify", returns='s')
    def Identify(self, c):
        '''Ask instrument to identify itself'''
        command = self.IdenStr()
        yield self.ser.write(command)
        yield self.ForceRead() # expect a reply from instrument
        answer = yield self.ser.readline()
        returnValue(answer[:-1])

    @setting(2, "Amplitude", level = 'v',returns = "v")
    def Amplitude(self, c, level=None):
        '''Sets power level, enter power in dBm'''
        if level is not None:
            self.checkPower(level)
            command = self.PowerSetStr(level)
            yield self.ser.write(command)
            self.marDict['power'] = level
            notified = self.getOtherListeners(c)
            self.onNewUpdate(('power',level),notified)
        returnValue(self.marDict['power'])
    
    @setting(3, "Frequency", freq = 'v', returns='v')
    def Frequency(self, c, freq=None):
        '''Get or set the CW frequency (MHz)'''
        if freq is not None:
            self.checkFreq(freq)
            command = self.FreqSetStr(freq)
            yield self.ser.write(command)
            self.marDict['freq'] = freq
            notified = self.getOtherListeners(c)
            self.onNewUpdate(('freq',freq),notified)
        returnValue(self.marDict['freq'])

    @setting(4, "Output_State", state= 'b', returns = "b")
    def Output_State(self, c, state=None):
        '''Get or set the on/off state of the CW signal'''
        if state is not None:
            command = self.OutputStateSetStr(state)
            yield self.ser.write(command)
            self.marDict['output_state'] = state
            notified = self.getOtherListeners(c)
            self.onStateUpdate(state,notified)
        returnValue(self.marDict['output_state'])    
    
    #@setting(8, "SetPowerUnits", units = 's', returns = '')
    #def SetPowerUnits(self, c=None, units='DBM'):
        #'''Sets power units, default is dBm'''
        #command = self.PowerUnitsSetStr(units)
        #yield self.ser.write(command)
        #self.marDict['power_units'] = units
        #notified = self.getOtherListeners(c)
        #self.onNewUpdate(('power_units',units),notified)

    @setting(10, "Clear", returns = '')
    def Clear(self, c=None):
        '''Clear the event register and error queue'''
        command = self.ClearStatusStr()
        yield self.ser.write(command)


    # ===== HIDDEN METHODS =====

    @inlineCallbacks
    def SetControllerMode(self, mode):
        command = self.SetModeStr(mode)
        yield self.ser.write(command)

    @inlineCallbacks
    def SetControllerWait(self, status):
        command = self.WaitRespStr(status)
        yield self.ser.write(command)

    @inlineCallbacks
    def SetEOIState(self, state):
        command = self.EOIStateStr(state)
        yield self.ser.write(command)

    @inlineCallbacks
    def ForceRead(self):
        command = self.ForceReadStr()
        yield self.ser.write(command)
    
    @inlineCallbacks
    def _GetState(self):
        command = self.OutputStateReqStr()
        yield self.ser.write(command)
        yield self.ForceRead() # expect a reply from instrument
        print 'HERE'
        response = yield self.ser.readline()
        #print "response is: ", str(response)
        #state_str = str(response).split(':')[2]
        #if state_str == 'ENABLE':
        #    state = True
        #else:
        #    state = False
        returnValue(response)
    
    def parseState(self, msg):
        if msg == '':
            raise Exception("State response is ''.")
        return msg.split(":")[1]

    @inlineCallbacks
    def _GetFreq(self):
        command = self.FreqReqStr()
        yield self.ser.write(command)
        yield self.ForceRead() # expect a reply from instrument
        response = yield self.ser.readline()
        freq = 1 # float(response.split(';')[0].split()[1]) / 10**6 # freq is in MHz
        returnValue(response)
    
    @inlineCallbacks
    def _GetPower(self):
        command = self.PowerReqStr()
        yield self.ser.write(command)
        yield self.ForceRead() # expect a reply from instrument
        response = yield self.ser.readline()
        amp = 1 # float(response.split(';')[2].split()[1])
        returnValue(response)
    
    def checkPower(self, level):
        MIN, MAX = self.marDict['power_range']
        if not MIN <= level <= MAX:
            raise Exception('Power out of allowed range')

    def checkFreq(self, freq):
        MIN, MAX = self.marDict['freq_range']
        if not MIN <= freq <= MAX:
            raise Exception('Frequency out of allowed range')


    # ===== MARCONI STR MESSAGES =====

    def IdenStr(self):
        '''String to request machine to identify itself'''
        return '*IDN?' + '\n'
 
    def ClearStatusStr(self):
        '''String to clear the envent register and error queue'''
        return '*CLS' + '\n'

    def FreqReqStr(self):
        '''String to request current frequency'''
        return 'CFRQ?' + '\n'
        
    def FreqSetStr(self,freq):
        '''String to set freq (in MHZ)'''
        return 'CFRQ:Value ' + str(freq) + 'MHZ' + '\n'
         
    def OutputStateReqStr(self):
        '''String to request on/off'''
        return 'OUTPUT?' + '\n'

    def OutputStateSetStr(self, state):
        '''String to set state on/off'''
        if state:
            return 'OUTPUT:ENABLE' + '\n'
        else:
            return 'OUTPUT:DISABLE' + '\n'

    def PowerReqStr(self):
        '''String to request current power'''
        return 'RFLV?' + '\n'

    def PowerSetStr(self,pwr):
        '''String to set power (in dBm)'''
        return 'RFLV:Value ' +str(pwr) + ' DBM' + '\n'
        
    #def PowerUnitsSetStr(self, units='DBM'):
        #'''String to set power units (defaults to dBM)'''
        #return 'RFLV:UNITS ' + units


    # ===== PROLOGIX STR MESSAGES =====

    def ForceReadStr(self):
        '''String to force progolix to read device response'''
        return '++read eoi' + '\n'

    def WaitRespStr(self, wait):
        '''String for prologix to request a response from instrument'''
        return '++auto ' + str(wait) + '\n'

    def EOIStateStr(self, state):
        '''String to enable/disable EOI assertion with last character.
        State = 1 for enable, 0 for disable.'''
        return '++eoi ' + str(state) + '\n'
    
    def SetAddrStr(self, addr):
        '''String to set addressing of prologix'''
        return '++addr ' + str(addr) + '\n'

    def SetModeStr(self, mode):
        '''String to set prologix to CONTROLLER (1), or DEVICE (0) mode'''
        return '++mode ' + str(mode) + '\n'


if __name__ == "__main__":
    from labrad import util
    util.runServer(MarconiServer())
