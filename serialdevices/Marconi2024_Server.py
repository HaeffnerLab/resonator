# MarconiServer, serial version
# Requires serial_server_v1_2.py (serial device manager) to be running in labrad

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

from serialdeviceserver import SerialDeviceServer
from serialdeviceserver import SerialDeviceError, SerialConnectionError
from serialdeviceserver import setting, inlineCallbacks
from twisted.internet.defer import returnValue

# Default Startup Values
ON_OFF = True
AMP = -30
FREQ = 1

CARRIER_MODE = 'FIXED'
SWEEP_RANGE_START = 1
SWEEP_RANGE_STOP = 2
SWEEP_STEP = 0.05
SWEEP_TIME = 50
SWEEP_MODE = 'SNGL'
SWEEP_SHAPE = 'LIN'
SWEEP_TRIG_MODE = 'OFF'

# Marconi Extreme Values, don't change
FREQ_MIN = 0.009    # 9 KHz
FREQ_MAX = 2400     # 2400 MHz
POWER_MIN = -137    # -137 dBm
POWER_MAX = 10      # 10 dBm

# CONSTANTS used by SweepRangeException, don't change
START = 0
STOP = 1

class MarconiServer(SerialDeviceServer):
    """Server for basic CW control of Marconi RF Generator"""
    # set MarconiKey in reg to ttyUSB# (# is USB port connection)

    name = 'Marconi Server'
    regKey = 'MarconiKey' 
    port = None
    serNode = 'resonatormain' # labradnode
    timeout = 1.0
    gpibaddr = 11

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

        yield self.ser.write(self.SetAddrStr(self.gpibaddr)) # set gpib address
        yield self._SetControllerWait(0)   # turn off auto listen after talk 
        self.SetInitialValues()

    def createDict(self):
        d = {}

        # == BASIC SETTINGS ==
        d['on_off'] = None                      # True (ON) or False (OFF)
        d['power'] = None                       # power in dBm
        d['power_min'] = POWER_MIN              # min power in dBm
        d['power_max'] = POWER_MAX              # max power in dBm
        d['freq'] = None                        # frequency in MHz
        d['freq_min'] = FREQ_MIN                # min freq  in MHz
        d['freq_max'] = FREQ_MAX                # max freq in MHz

        # == SWEEP SETTINGS ==
        d['carrier_mode'] = None                # True (FIXED) or False (SWEPT)
        d['sweep_range_start'] = None           # start freq in MHz
        d['sweep_range_stop'] = None            # stop freq in MHz
        d['sweep_step'] = None                  # freq step in MHz
        d['sweep_time'] = None                  # time per step in ms
        d['sweep_mode'] = None                  # True (SNGL) or False (CONT)
        d['sweep_shape'] = None                 # True (LIN) or False (LOG)
        d['trig_mode'] = None                   # See SweepTrigModeSetStr
        d['currently_sweeping'] = None          # True if currently sweeping
        self.marDict = d
    
    def SetInitialValues(self):
        self._CarrierOnOff(ON_OFF)
        self._Amplitude(AMP)
        self._Frequency(FREQ)
        self._CarrierMode(CARRIER_MODE)
        self._SweepRangeStart(SWEEP_RANGE_START)
        self._SweepRangeStop(SWEEP_RANGE_STOP)
        self._SweepStep(SWEEP_STEP)
        self._SweepTime(SWEEP_TIME)
        self._SweepMode(SWEEP_MODE)
        self._SweepShape(SWEEP_SHAPE)
        self._SweepTrigMode(SWEEP_TRIG_MODE)

    # +++++++++++++++++++++++++++
    # ===== BASIC SETTINGS ======
    # +++++++++++++++++++++++++++

    @setting(10, "Identify", returns = 's')
    def Identify(self, c):
        '''Ask instrument to identify itself'''
        return self._Identify()

    @setting(11, "CarrierOnOff", state = 'b', returns = 'b')
    def CarrierOnOff(self, c, state=None):
        '''Get or set the on/off state of the CW signal'''       
        return self._CarrierOnOff(state)

    @setting(12, "Amplitude", level = 'v', returns = "v")
    def Amplitude(self, c, level=None):
        '''Get or set the power level (dBm)'''
        return self._Amplitude(level)
    
    @setting(13, "Frequency", freq = 'v', returns='v')
    def Frequency(self, c, freq=None):
        '''Get or set the CW frequency (MHz)'''
        return self._Frequency(freq)
        

    # ++++++++++++++++++++++++++++
    # ===== SWEEP SETTINGS  ======
    # ++++++++++++++++++++++++++++

    @setting(20, "CarrierMode", mode = 's', returns = 's') # or 's'
    def CarrierMode(self, c, mode=None):
        '''Get or set the carrier mode to 'FIXED' or 'SWEPT' '''
        return self._CarrierMode(mode)

    @setting(21, "SweepRangeStart", start = 'v', returns = 'v')
    def SweepRangeStart(self, c, start=None):
        '''Get or set the starting point for carrier frequency sweeps (MHZ)'''
        return self._SweeoRangeStart(start)

    @setting(22, "SweepRangeStop", stop = 'v', returns = 'v')
    def SweepRangeStop(self, c, stop=None):
        '''Get or set the ending point for carrier frequency sweeps (MHZ)'''
        return self._SweepRangeStop(stop)

    @setting(23, "SweepStep", step = 'v', returns = 'v')
    def SweepStep(self, c, step=None):
        '''Get or set the sweep step (MHZ)'''
        return self._SweepStep(step)

    @setting(24, "SweepTime", time = 'v', returns = 'v')
    def SweepTime(self, c, time=None):
        '''Get or set the time to complete one sweep step (ms)'''
        return self._SweepTime(time)

    @setting(25, "SweepMode", mode = 's', returns = 's')
    def SweepMode(self, c, mode=None):
        '''Get or set the sweep mode to single shot (SNGL) or continuous (CONT)'''
        return self._SweepMode(mode)

    @setting(26, "SweepShape", shape = 's', returns = 's')
    def SweepShape(self, c, shape=None):
        '''Get or set the sweep shape to linear (LIN) of log (LOG)'''
        return self._SweepShape(shape)

    @setting(27, "SweepTrigMode", trig_mode = 's', returns = 's')
    def SweepTrigMode(self, c, trig_mode=None):
        '''Get or set the external trigger mode.
        Options are: OFF, START, STARTSTOP, STEP'''
        return self._SweepTrigMode(trig_mode)

    @setting(30, "SweepBegin", returns = '')
    def SweepBegin(self, c):
        '''Start a sweep'''
        return self._SweepBegin()

    @setting(31, "SweepPause", returns = '')
    def SweepPause(self, c):
        '''Pause the current sweep'''
        return self._SweepPause()

    @setting(32, "SweepContinue", returns = '')
    def SweepContinue(self, c):
        '''Continue the currently paused sweep'''
        return self._SweepContinue()

    @setting(33, "SweepReset", returns = '')
    def SweepReset(self, c):
        '''Reset the current sweep to the start frequency'''
        return self._SweepReset()


    # ++++++++++++++++++++++++++
    # ===== HIDDEN METHODS =====
    # ++++++++++++++++++++++++++

    # ===== BASIC =====

    @inlineCallbacks
    def _Identify(self):
        '''Ask instrument to identify itself'''
        command = self.IdenStr()
        yield self.ser.write(command)
        yield self._ForceRead()
        answer = yield self.ser.readline()
        returnValue(answer[:-1])

    @inlineCallbacks
    def _CarrierOnOff(self, state=None):
        '''Get or set the on/off state of the CW signal'''
        if state is not None:
            command = self.CarrierOnOffSetStr(state)
            yield self.ser.write(command)
            self.marDict['on_off'] = state
        returnValue(self.marDict['on_off'])

    @inlineCallbacks
    def _Amplitude(self, level=None):
        '''Sets power level, enter power in dBm'''
        if level is not None:
            checkedLevel = self.checkPower(level)
            command = self.PowerSetStr(checkedLevel)
            yield self.ser.write(command)
            self.marDict['power'] = checkedLevel
        returnValue(self.marDict['power'])
    
    def checkPower(self, level):
        if level < self.marDict['power_min']:
            print "*** WARNING: attempt to set power below minimum value."
            print "*** WARNING: setting to minimum value instead."
            return self.marDict['power_min']
        elif level > self.marDict['power_max']:
            print "*** WARNING: attempt to set power above maximum value."
            print "*** WARNING: setting to maximum value instad."
            return self.marDict['power_max']
        return level

    @inlineCallbacks
    def _Frequency(self, freq=None):
        '''Get or set the CW frequency (MHz)'''
        if freq is not None:
            checkedFreq = self.checkFreq(freq)
            command = self.FreqSetStr(checkedFreq)
            yield self.ser.write(command)
            self.marDict['freq'] = checkedFreq
        returnValue(self.marDict['freq'])

    def checkFreq(self, freq):
        if freq < self.marDict['freq_min']:
            print "*** WARNING: attempt to set frequency below minimum value."
            print "*** WARNING: setting to minimum value instead."
            return self.marDict['freq_min']
        elif freq > self.marDict['freq_max']:
            print "*** WARNING: attempt to set frequency above maximum value."
            print "*** WARNING: setting to maximum value instad."
            return self.marDict['freq_max']
        return freq

    # ===== SWEEP =====

    @inlineCallbacks
    def _CarrierMode(self, mode=None):
        '''Get or set the carrier mode to 'FIXED' or 'SWEPT' '''
        if mode is not None:
            if mode not in ('FIXED', 'SWEPT'):
                raise ValueError("Carrier mode must be 'FIXED', or 'SWEPT'")
            command = self.CarrierModeSetStr(mode)
            yield self.ser.write(command)
            self.marDict['carrier_mode'] = mode
        returnValue(self.marDict['carrier_mode'])
    
    #class SweepRangeException(Exception):
        #'''Raise when start frequency is greater than or equal to stop
        #frequency. Contains information about whether the user attempted
        #to set the start above stop, or stop below start. This is encoded in
        #the wasUpdating field, which should use the values START and STOP.'''

        #def __init__(self, wasUpdating, msg=None):
            #super(SweepRangeException, self).__init__(msg)
            #wasUpdating = wasUpdating

    @inlineCallbacks
    def _SweepRangeStart(self, start=None):
        '''Get or set the starting point for carrier frequency sweeps (MHZ).
        Car raise SweepRangeException(START)'''
        if start is not None:
            #self.checkCarrierMode()
            checkedStart = self.checkFreq(start)
            #if checkedStart > self.marDict['sweep_range_stop']:
                #raise SweepRangeException(START, "Sweep start frequency cannot"\
                                            #+ "be greater than stop frequency")
            command = self.SweepStartSetStr(checkedStart)
            yield self.ser.write(command)
            self.marDict['sweep_range_start'] = checkedStart
        returnValue(self.marDict['sweep_range_start'])

    @inlineCallbacks
    def _SweepRangeStop(self, stop=None):
        '''Get or set the stoping point for carrier frequency sweeps (MHZ).
        Car raise SweepRangeException(STOP)'''
        if stop is not None:
            #self.checkCarrierMode()
            checkedStop = self.checkFreq(stop)
            #if checkedStop < self.marDict['sweep_range_start']:
                #raise SweepRangeException(STOP, "Sweep stop frequency cannot"\
                                            #+ "be smaller than start frequency")
            command = self.SweepStartSetStr(checkedStop)
            yield self.ser.write(command)
            self.marDict['sweep_range_stop'] = checkedStop
        returnValue(self.marDict['sweep_range_stop'])

    @inlineCallbacks
    def _SweepStep(self, step=None):
        '''Get or set the sweep step (MHz)'''
        if step is not None:
            #self.checkCarrierMode()
            command = self.SweepStepSetStr(step)
            yield self.ser.write(command)
            self.marDict['sweep_step'] = step
        returnValue(self.marDict['sweep_step'])

    @inlineCallbacks
    def _SweepTime(self, time=None):
        '''Get or set the time to complete one sweep step (ms)'''
        if time is not None:
            #self.checkCarrierMode()
            command = self.SweepTimeSetStr(time)
            yield self.ser.write(command)
            self.marDict['sweep_time'] = time
        returnValue(self.marDict['sweep_time'])

    @inlineCallbacks
    def _SweepMode(self, mode=None):
        '''Get or set the sweep mode to single (SNGL) or continuous (CONT)'''
        if mode is not None:
            #self.checkCarrierMode()
            command = self.SweepModeSetStr(mode)
            yield self.ser.write(command)
            self.marDict['sweep_mode'] = mode
        returnValue(self.marDict['sweep_mode'])

    @inlineCallbacks
    def _SweepShape(self, shape=None):
        '''Get or set the sweep shape to linear (LIN) of log (LOG)'''
        if shape is not None:
            #self.checkCarrierMode()
            command = self.SweepShapeSetStr(shape)
            yield self.ser.write(command)
            self.marDict['sweep_shape'] = shape
        returnValue(self.marDict['sweep_shape'])

    @inlineCallbacks
    def _SweepTrigMode(self, trig_mode=None):
        '''Get or set the external trigger mode.
        Options are: OFF, START, STARTSTOP, STEP'''
        if trig_mode is not None:
            #self.checkCarrierMode()
            command = self.SweepTrigModeSetStr(trig_mode)
            yield self.ser.write(command)
            self.marDict['trig_mode'] = trig_mode
        returnValue(self.marDict['trig_mode'])

    class CarrierModeException(Exception):
        '''Raised when attempting to access sweep functionality while
        CarrierMode is 'FIXED'. Contains the current CarrierMode as the
        field 'currentMode'.'''

        def __init__(self, msg=None):
            super(CarrierModeException, self).__init__(msg)
            currentMode = self.marDict['carrier_mode']

    def checkCarrierMode(self):
        '''Throws a CarrierModeException if the carrier mode is not 'SWEPT'.
        Carrier mode must be swept before other sweep methods are used.'''
        if self.marDict['carrier_mode'] != 'SWEPT':
            raise CarrierModeException("Carrier mode is not 'SWEPT'")

    @inlineCallbacks
    def _SweepBegin(self):
        '''Start a sweep'''
        self.checkCarrierMode()
        command = self.SweepBeginStr()
        yield self.ser.write(command)

    @inlineCallbacks
    def _SweepPause(self):
        '''Pause the current sweep'''
        self.checkCarrierMode()
        command = self.SweepPauseStr()
        yield self.ser.write(command)

    @inlineCallbacks
    def _SweepContinue(self):
        '''Continue the currently paused sweep'''
        self.checkCarrierMode()
        command = self.SweepContinueStr()
        yield self.ser.write(command)

    @inlineCallbacks
    def _SweepReset(self):
        '''Reset the current sweep to the start frequency'''
        self.checkCarrierMode()
        command = self.SweepResetStr()
        yield self.ser.write(command)

    # ===== META =====

    

    # ===== PROLOGIX =====

    @inlineCallbacks
    def _ForceRead(self):
        command = self.ForceReadStr()
        yield self.ser.write(command)

    @inlineCallbacks
    def _SetControllerWait(self, status):
        command = self.WaitRespStr(status)
        yield self.ser.write(command)

    @inlineCallbacks
    def _SetEOIState(self, state):
        command = self.EOIStateStr(state)
        yield self.ser.write(command)

    @inlineCallbacks
    def _SetAddr(self):
        command = self.SetAddrStr(self.gpibaddr)
        yield self.ser.write(command)


    # ++++++++++++++++++++++++++++++++
    # ===== MARCONI STR MESSAGES =====
    # ++++++++++++++++++++++++++++++++

    # ===== BASIC =====
    
    def IdenStr(self):
        '''String to request machine to identify itself'''
        return '*IDN?' + '\n'

    def CarrierOnOffReqStr(self):
        '''String to request carrier on/off state'''
        return 'RFLV?' + '\n'

    def CarrierOnOffSetStr(self, state):
        '''String to set carrier state on/off. True (ON) or False (OFF)'''
        if state:
            return 'RFLV:ON' + '\n'
        else:
            return 'RFLV:OFF' + '\n'
     
    def PowerReqStr(self):
        '''String to request current power'''
        return 'RFLV?' + '\n'

    def PowerSetStr(self, pwr):
        '''String to set power (in dBm)'''
        return 'RFLV:Value ' + str(pwr) + ' DBM' + '\n'

    def FreqReqStr(self):
        '''String to request current frequency'''
        return 'CFRQ?' + '\n'
        
    def FreqSetStr(self,freq):
        '''String to set freq (in MHZ)'''
        return 'CFRQ:Value ' + str(freq) + 'MHZ' + '\n'


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
        '''String to set frequency step size for carrier sweep (KHZ)'''
        return 'SWEEP:INC ' + str(step) + ' KHZ' + '\n'

    def SweepTimeSetStr(self, time):
        '''String to set time to complete a step of carrier sweep (S)'''
        return 'SWEEP:TIME ' + str(time) + ' MS' + '\n'

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
            raise ValueError("Sweep trigger mode must be one of: "\
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

if __name__ == "__main__":
    from labrad import util
    util.runServer(MarconiServer())
