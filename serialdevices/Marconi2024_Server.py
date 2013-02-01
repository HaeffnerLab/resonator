# Serial version
# Requires serial_server_v1_2.py to be running in labrad
# Simply inherits from serialdeviceserver
#
# onNewUpdate and onStateUpdate are for "notifying" when settings change
# this is because the OUTPUT:ENABLE/DISABLE capability allows updates
# to be grouped together to be changed all at once

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

    frequency_range = (0, 2400)     # (low, high) in MHZ
    power_range = (-137, 15)        # (low, high) in DBM

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
        ##for i in range(20):               # this method of force clearing
        ##    yield self.ForceRead()        # the buffer does not work!
        ##    yield self.ser.readline()
        yield self.populateDict()
        self._Reset()
        self.listeners = set()

    def createDict(self):
        d = {}
        d['carrier_state'] = None # state is boolean
        d['freq'] = None # frequency in MHz
        d['power'] = None # power in dBm
        #d['power_units'] = None # power (will be) in dBm
        d['power_range'] = power_range #None
        d['freq_range'] = freq_range #None
        d['carrier_mode'] = None # FIXED or SWEPT
        d['sweep_range'] = None # [start, stop] in MHZ
        d['sweep_step'] = None # MHZ
        d['sweep_time'] = None # Seconds
        d['sweep_mode'] = None # Single shot sweep (SNGL) or continuous (CONT)
        d['sweep_shape'] = None # Linear (LIN) or logarithmic (LOG)
        d['trig_mode'] = None # See SweepTrigModeSetStr
        d['currently_sweeping'] = None # True if currently sweeping
        self.marDict = d
    
    @inlineCallbacks
    def populateDict(self):
        stateStr = yield self._GetState() 
        freqStr = yield self._GetFreq()
        powerStr = yield self._GetPower()
        state = self.parseState(stateStr)
        freq = self.parseFreq(freqStr)
        power = self.parsePower(powerStr)
        
        self.marDict['carrier_state'] = bool(state) 
        self.marDict['power'] = float(power)
        self.marDict['freq'] = float(freq)
        #self.marDict['power_units'] = 'DBM' # default
        #self.marDict['power_range'] = [-100, 13] already set
        #self.marDict['freq_range'] = [0, 1000] already set
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)
        
    def getOtherListeners(self, c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified
    

    # +++++++++++++++++++++++++++
    # ===== BASIC SETTINGS ======
    # +++++++++++++++++++++++++++

    @setting(10, "Identify", returns = 's')
    def Identify(self, c):
        '''Ask instrument to identify itself'''
        command = self.IdenStr()
        yield self.ser.write(command)
        yield self.ForceRead() # expect a reply from instrument
        answer = yield self.ser.readline()
        returnValue(answer[:-1])

    @setting(11, "Amplitude", level = 'v', returns = "v")
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
    
    @setting(12, "Frequency", freq = 'v', returns='v')
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

    @setting(13, "CarrierState", state = 'b', returns = 'b')
    def CarrierState(self, c, state=None):
        '''Get or set the on/off state of the CW signal'''
        if state is not None:
            command = self.CarrierStateSetStr(state)
            yield self.ser.write(command)
            self.marDict['carrier_state'] = state
            notified = self.getOtherListeners(c)
            self.onStateUpdate(state,notified)
        returnValue(self.marDict['carrier_state'])    

    #@setting(14, "SetPowerUnits", units = 's', returns = '')
        #def SetPowerUnits(self, c=None, units='DBM'):
            #'''Sets power units, default is dBm'''
            #command = self.PowerUnitsSetStr(units)
            #yield self.ser.write(command)
            #self.marDict['power_units'] = units
            #notified = self.getOtherListeners(c)
            #self.onNewUpdate(('power_units',units),notified)

    # ++++++++++++++++++++++++++++
    # ===== SWEEP SETTINGS  ======
    # ++++++++++++++++++++++++++++

    @setting(21, "CarrierMode", mode = 's', returns = 's') # or 's'
    def CarrierMode(self, c, mode=None):
        '''Get or set the carrier mode to 'FIXED' or 'SWEPT' '''
        if mode is not None:
            command = self.CarrierModeSetStr(self, mode)
            yield self.ser.write(command)
            self.marDict['carrier_mode'] = mode
        returnValue(self.marDict['carrier_mode'])

    def checkCarrierMode(self, setting):
        '''Throws an exception if carrier mode is not 'FIXED'. Carrier mode
        must be 'FIXED' before any other sweep method is used.'''
        if self.marDict['carrier_mode'] != 'FIXED':
            raise Exception("Carrier mode must be 'FIXED' to use"\
                            + " other sweep methods")

    @setting(22, "SweepRange", start = 'v', stop = 'v', returns = '*v')
    def SweepRange(self, c, start=None, stop=None):
        '''Get or set the frequency sweep range, start to stop (MHZ)'''
        self.checkCarrierMode()
        if start is None and stop is not None:
            start = self.marDict['sweep_range'][0]
        elif start is not None and stop is None:
            stop = self.marDict['sweep_range'][1]
        
        if start is not None and stop is not None:
            if start <= stop:
                raise ValueError("Sweep start frequency must be greater"\
                                 + "than stop frequency")
            self.checkFreq(start)
            self.checkFreq(stop)
            command1 = self.SweepStartSetStr(start)
            command2 = self.SweepStopSetStr(stop)
            yield self.ser.write(command1)
            yield self.ser.write(command2)
            self.marDict['sweep_range'][0] = start
            self.marDict['sweep_range'][1] = stop
        return self.marDict['sweep_range']

    @setting(23, "SweepStep", step = 'v', returns = 'v')
    def SweepStep(self, c, step=None):
        '''Get or set the sweep step (MHZ)'''
        self.checkCarrierMode()
        if step is not None:
            command = self.SweepStepSetStr(step)
            yield self.ser.write(command)
            self.marDict['sweep_step'] = step
        return self.marDict['sweep_step']

    @setting(24, "SweepTime", time = 'v', returns = 'v')
    def SweepTime(self, c, time=None):
        '''Get or set the time to complete one sweep step (Seconds)'''
        self.checkCarrierMode()
        if time is not None:
            command = self.SweepTimeSetStr(time)
            yield self.ser.write(command)
            self.marDict['sweep_time'] = time
        return self.marDict['sweep_time']

    @setting(25, "SweepMode", mode = 's', returns = 's')
    def SweepMode(self, c, mode=None):
        '''Get or set the sweep mode to single shot (SNGL) or continuous (CONT)'''
        self.checkCarrierMode()
        if mode is not None:
            command = self.SweepModeSetStr(mode)
            yield self.ser.write(command)
            self.marDict['sweep_mode'] = mode
        return self.marDict['sweep_mode']

    @setting(26, "SweepShape", shape = 's', returns = 's')
    def SweepShape(self, c, shape=None):
        '''Get or set the sweep shape to linear (LIN) of log (LOG)'''
        self.checkCarrierMode()
        if shape is not None:
            command = self.SweepShapeSetStr(shape)
            yield self.ser.write(command)
            self.marDict['sweep_shape'] = shape
        return self.marDict['sweep_shape']

    @setting(27, "SweepTrigMode", tig_mode = 's', returns = 's')
    def SweepTrigMode(self, c, trig_mode=None):
        '''Get or set the external trigger mode.
        Options are: OFF, START, STARTSTOP, STEP'''
        self.checkCarrierMode()
        if trig_mode is not None:
            command = self.SweepTrigModeSetStr(tig_mode)
            yield self.ser.write(command)
            self.marDict['trig_mode'] = trig_mode
        return self.marDict['trig_mode']

    @setting(28, "SweepBegin", returns = '')
    def SweepBegin(self, c):
        '''Start a sweep'''
        self.checkCarrierMode()
        command = self.SweepBeginStr()
        yield self.ser.write(command)

    @setting(29, "SweepPause", returns = '')
    def SweepPause(self, c):
        '''Pause the current sweep'''
        self.checkCarrierMode()
        command = self.SweepPauseStr()
        yield self.ser.write(command)

    @setting(30, "SweepContinue", returns = '')
    def SweepContinue(self, c):
        '''Continue the currently paused sweep'''
        self.checkCarrierMode()
        command = self.SweepContinueStr()
        yield self.ser.write(command)

    @setting(31, "SweepReset", returns = '')
    def SweepReset(self, c):
        '''Reset the current sweep to the start frequency'''
        self.checkCarrierMode()
        command = self.SweepResetStr()
        yield self.ser.write(command)


    # +++++++++++++++++++++++++
    # ===== META SETTINGS =====
    # +++++++++++++++++++++++++

    @setting(100, "Clear", returns = '')
    def Clear(self, c):
        '''Clear the event register and error queue'''
        command = self.ClearStatusStr()
        yield self.ser.write(command)

    
    @setting(101, "GetStatusByte", returns = 's')
    def GetStatusByte(self, c):
        '''Return the status byte. Especially useful is the error queue bit (7)
        which is 1 if there are errors in the error event queue and 0 otherwise.
        This can be reset with Clear().'''
        command = self.StatusByteReqStr()
        yield self.ser.write(command)
        yield self.ForceRead()
        response = yield self.ser.readline()
        try:
            bits = bin(int(response))[2:]
            statusbyte = '0'*(8-len(bits)) + bits
        except ValueError:
            statusbyte = 'buffernotcleared'
        returnValue(statusbyte)
    
    @setting(102, "Reset", returns = '')
    def Reset(self, c):
        '''Resets to factory settings'''
        self._Reset()

    #@setting(1000, "GetState", returns = 's')
    #def GetState(self, c):
        #command = self.CarrierStateReqStr()
        #yield self.ser.write(command)
        #yield self.ForceRead() # expect a reply from instrument
        #response = yield self.ser.readline()
        #returnValue(response)

    # ++++++++++++++++++++++++++
    # ===== HIDDEN METHODS =====
    # ++++++++++++++++++++++++++

    # ===== META =====

    @inlineCallbacks
    def _Reset(self):
        command = self.ResetStr()
        yield self.ser.write(command)
        yield self.ForceRead()
        self.marDict['carrier_state'] = True
        self.marDict['power'] = -137
        self.marDict['freq'] = 2400

    # ===== PROLOGIX =====

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
    
    # ===== BASIC =====

    @inlineCallbacks
    def _GetCarrierState(self):
        command = self.CarrierStateReqStr()
        yield self.ser.write(command)
        yield self.ForceRead() # expect a reply from instrument
        response = yield self.ser.readline()
        returnValue(response)
    
    @ann
    def parseState(self, msg):
        #if msg == '':
        #    raise Exception("State response is ''")
        #state_str =  msg.split(':')[1]
        state_str = 'ON'
        if state_str == 'ON':
            state = True
        else:
            state = False
        return state

    @inlineCallbacks
    def _GetFreq(self):
        command = self.FreqReqStr()
        yield self.ser.write(command)
        yield self.ForceRead() # expect a reply from instrument
        response = yield self.ser.readline()
        returnValue(response)
    
    @ann
    def parseFreq(self, msg):
        #if msg == '':
        #    raise Exception("Frequency response is ''")
        #freq = float(msg.split(';')[0].split()[1]) / 10**6 # freq is in MHz
        freq = 1
        return freq
    
    @inlineCallbacks
    def _GetPower(self):
        command = self.PowerReqStr()
        yield self.ser.write(command)
        yield self.ForceRead() # expect a reply from instrument
        response = yield self.ser.readline()
        returnValue(response)
    
    @ann
    def parsePower(self, msg):
        #if msg == '':
        #    raise Exception("Frequency response is ''")
        #amplitude = float(msg.split(';')[2].split()[1])
        amplitude = 1
        return amplitude

    def checkPower(self, level):
        MIN, MAX = self.marDict['power_range']
        if not MIN <= level <= MAX:
            raise Exception('Power out of allowed range')

    def checkFreq(self, freq):
        MIN, MAX = self.marDict['freq_range']
        if not MIN <= freq <= MAX:
            raise Exception('Frequency out of allowed range')

    # ===== SWEEP =====




    # ++++++++++++++++++++++++++++++++
    # ===== MARCONI STR MESSAGES =====
    # ++++++++++++++++++++++++++++++++

    # ===== META =====
    
    def IdenStr(self):
        '''String to request machine to identify itself'''
        return '*IDN?' + '\n'
 
    def ClearStatusStr(self):
        '''String to clear the event register and error queue'''
        return '*CLS' + '\n'

    def StatusByteReqStr(self):
        '''String to request the status byte'''
        return '*STB?' + '\n'

    def ResetStr(self):
        '''String to reset to factory settings'''
        return '*RST' + '\n'

    # ===== BASIC =====

    def FreqReqStr(self):
        '''String to request current frequency'''
        return 'CFRQ?' + '\n'
        
    def FreqSetStr(self,freq):
        '''String to set freq (in MHZ)'''
        return 'CFRQ:Value ' + str(freq) + 'MHZ' + '\n'
         
    def CarrierStateReqStr(self):
        '''String to request carrier on/off state'''
        return 'RFLV?' + '\n'

    def CarrierStateSetStr(self, state):
        '''String to set carrier state on/off'''
        if state:
            return 'RFLV:ON' + '\n'
        else:
            return 'RFLV:OFF' + '\n'

    def PowerReqStr(self):
        '''String to request current power'''
        return 'RFLV?' + '\n'

    def PowerSetStr(self,pwr):
        '''String to set power (in dBm)'''
        return 'RFLV:Value ' +str(pwr) + ' DBM' + '\n'

    #def PowerUnitsSetStr(self, units='DBM'):
            #'''String to set power units (defaults to dBM)'''
            #return 'RFLV:UNITS ' + '\n' + units
    
    # ===== SWEEP =====
    
    def CarrierModeSetStr(self, mode):
        '''String to set carrier to FIXED or SWEPT mode'''
        mode = mode.upper()
        if not mode in ('FIXED', 'SWEPT'):
            raise ValueError("Carrier mode is 'FIXED' or 'SWEPT'")
        return 'CFRQ:MODE ' + mode + '\n'

    def SweepStartSetStr(self, start):
        '''String to set starting frequency for carrier sweep (MHZ)'''
        return 'SWEEP:START ' + str(start) + ' MHZ' + '\n'

    def SweepStopSetStr(self, stop):
        '''String to set stopping frequency for carrier sweep (MHZ)'''
        return 'SWEEP:STOP ' + str(stop) + ' MHZ' + '\n'

    def SweepStepSetStr(self, step):
        '''String to set frequency step size for carrier sweep (MHZ)'''
        return 'SWEEP:INC ' + str(step) + ' MHZ' + '\n'

    def SweepTimeSetStr(self, time):
        '''String to set time to complete a step of carrier sweep (S)'''
        return 'SWEEP:TIME ' + str(step) + ' S' + '\n'

    def SweepModeSetStr(self, mode):
        '''String to set sweep mode to SNGL shot or CONT sweep'''
        mode = mode.upper()
        if not mode in ('SNGL', 'CONT'):
            raise ValueError("Sweep mode is 'SNGL' or 'CONT'")
        return 'SWEEP:MODE ' + mode + '\n'

    def SweepShapeSetStr(self, shape):
        '''String to set shape of sweep to linear (LIN) or logarithmic (LOG)'''
        shape = shape.upper()
        if not shape in ('LIN', 'LOG'):
            raise ValueError("Sweep shape is 'LIN' or 'LOG'")
        return 'SWEEP:TYPE ' + shape + '\n'

    def SweepTrigModeSetStr(self, trig_mode):
        '''String to set trigger mode to OFF, START, STARTSTOP, or STEP
        as described in the Marconi Manual'''
        trig_mode = trig_mode.upper()
        if not trig_mode in ('OFF', 'START', 'STARTSTOP', 'STEP'):
            raise ValueError("Sweep trigger mode is "\
                            "'OFF', 'START', 'STARTSTOP', or 'STEP'")
        return 'SWEEP:TRIG ' + trig_mode + '\n'

    def SweepBeginStr(self):
        '''String to begin sweeping'''
        return 'SWEEP:GO' + '\n'

    def SweepPauseStr(self):
        '''String to pause sweeping (at current location in sweep)'''
        return 'SWEEP:HALT' + '\n'

    def SweepContinueStr(self):
        '''String to continue sweeping (from pause point)'''
        return 'SWEEP:CONT' + '\n'

    def SweepResetStr(self):
        '''String to reset sweeping point to start'''
        return 'SWEEP:RESET' + '\n'

    # ===== PROLOGIX =====

    def ForceReadStr(self):
        '''String to force progolix to read device response'''
        return '++read eoi' + '\n'

    def WaitRespStr(self, wait):
        '''String for prologix to request a response from instrument'''
        return '++auto ' + str(wait) + '\n'

    def EOIStateStr(self, state):
        '''String to enable/disable EOI assertion with last character.
        State = 1 for enable, 0 for disable.'''
        return '++eoi ' +  str(state) + '\n'
    
    def SetAddrStr(self, addr):
        '''String to set addressing of prologix'''
        return '++addr ' +  str(addr) + '\n'

    def SetModeStr(self, mode):
        '''String to set prologix to CONTROLLER (1), or DEVICE (0) mode'''
        return '++mode ' + str(mode) + '\n'


if __name__ == "__main__":
    from labrad import util
    util.runServer(MarconiServer())
