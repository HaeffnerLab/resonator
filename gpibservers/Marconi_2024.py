# Ryan Blais
# To Do: test, output status functionality
# Questions: where to find docs on addCallback
"""
### BEGIN NODE INFO
[info]
name = Marconi Server (GPIB)
version = 1.0
description = 

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
from labrad.units import WithUnit
from labrad.types import Error


# Default Startup Values
ON_OFF = False
AMP = -30
FREQ = WithUnit(1,'MHz')
CARRIER_MODE = 'FIXED'
SWEEP_RANGE_START = WithUnit(1,'MHz')
SWEEP_RANGE_STOP = WithUnit(2,'MHz')
SWEEP_STEP = 0.05
SWEEP_TIME = 50
SWEEP_MODE = 'SNGL'
SWEEP_SHAPE = 'LIN'
SWEEP_TRIG_MODE = 'OFF'

# Startup with Default values
# Set to true to load Default values (above) at startup, rather than the
# MostRecentSettings saved from the previous session.
START_WITH_DEFAULTS = True

# Marconi Extreme Values (should be set according to
# the max and min values the marconi actually will allow).
FREQ_MIN = 0.009 # 9 KHz
FREQ_MAX = 2400 # 2400 MHz
POWER_MIN = -137 # -137 dBm
POWER_MAX = 10 # 10 dBm

class Marconi2024Wrapper(GPIBDeviceWrapper):

    @inlineCallbacks
    def initialize(self):
        yield self.createDict()
        
    @inlineCallbacks
    def createDict(self):
        """Creates dictionary to store Marconi settings."""
        d = {}

        # == BASIC SETTINGS ==
        d['on_off'] = yield self.requestRF() # True (ON) or False (OFF)
        d['power'] = yield self.getAmplitude() # power in dBm
        d['power_min'] = POWER_MIN # min power in dBm
        d['power_max'] = POWER_MAX # max power in dBm
        d['freq'] = yield self.getFrequency() # frequency in MHz
        d['freq_min'] = FREQ_MIN # min freq in MHz
        d['freq_max'] = FREQ_MAX # max freq in MHz

        # == SWEEP SETTINGS ==
        d['carrier_mode'] = None # True (FIXED) or False (SWEPT)
        d['sweep_range_start'] = None # start freq in MHz
        d['sweep_range_stop'] = None # stop freq in MHz
        d['sweep_step'] = None # freq step in MHz
        d['sweep_time'] = None # time per step in ms
        d['sweep_mode'] = None # True (SNGL) or False (CONT)
        d['sweep_shape'] = None # True (LIN) or False (LOG)
        d['trig_mode'] = None # See SweepTrigModeSetStr
        #d['currently_sweeping'] = None # True if currently sweeping
        self.marDict = d
        print self.marDict['freq']
        print self.marDict['power']
        

    
    @inlineCallbacks
    def setupRegistry(self):
        """Establish access to registry server."""
        # Get access to registry server
        self.reg = yield self.client.registry
        # Create directory structure (for saving settings) if it does not exist
        self.reg.cd('')
        self.reg.cd(['Servers','Marconi Server','Settings'], True)

    @inlineCallbacks
    def setInitialValues(self):
        """
        Load and/or set the initial values for the marconi.
        These settings are written to the marconi, not loaded from its
        current values. If there is a set of saved settings called 'Default',
        and the key 'Use Default' is set to True under MarconiServer in the
        registry, then the default will be used. Otherwise the settings in
        'MostRecentSettings' will be used. As a last resort the defaults
        given at the top of this file are loaded.
        """
        # Find available settings
        self.reg.cd(self.regPath + ['Settings'])
        settings = yield self.reg.dir()
        settings = settings[1]
        # Determine whether to use default settings
        self.reg.cd(self.regPath)
        try:
            use_default = yield self.reg.get('Use Default')
        except Error:
            use_default = False
        # Load appropriate settings
        if 'Default' in settings and use_default:
            print("Loading settings in Default.")
            self._LoadSettings('Default')
        elif 'MostRecentSettings' in settings:
            print("Loading settings in MostRecentSettings.")
            self._LoadSettings('MostRecentSettings')
        else:
            print("User's default settings and MostRecentSettings not detected.")
            print("Using builtin default settings instead.")
            self.setDefaultValues()

    def setDefaultValues(self):
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

    def stopServer(self):
        """Save current server settings in 'MostRecentSettings' in registry. """
        self._SaveSettings('MostRecentSettings')

    # ++++++++++++++++++++++++++
    # ===== HIDDEN METHODS =====
    # ++++++++++++++++++++++++++

    # ===== META =====

    @inlineCallbacks
    def _SaveSettings(self, saveName):
        """Saves current server settings in the LabRAD registry in:
        ['','Servers','Marconi Server', 'Settings', saveName]."""
        print "Saving settings to: " + str(self.regPath + ['Settings', saveName])
        # enter save directory, creating if doesn't exist
        yield self.reg.cd(self.regPath + ['Settings',saveName], True)
        # save each marDict key as a registry key with associated value
        for setting in self.marDict:
            self.reg.set(setting,self.marDict[setting])
        self.reg.cd('')

    @inlineCallbacks
    def _LoadSettings(self, loadName):
        """Loads previous server settings from loadName in the registry."""
        print "Loading settings from: " + str(self.regPath + ['Settings', loadName])
        yield self.reg.cd(self.regPath + ['Settings',loadName])
        for setting in self.marDict:
            self.marDict[setting] = yield self.reg.get(setting)
        print self.marDict
        self.reg.cd('')

    # ===== BASIC =====

    @property
    def frequency(self):
        return self.marDict['freq']
    
    @property
    def amplitude(self):
        return self.marDict['power']

    @inlineCallbacks
    def _Identify(self):
        """Ask instrument to identify itself"""
        command = self.IdenStr()
        answer = yield self.query(command)
        returnValue(answer[:-1])

    @inlineCallbacks
    def _CarrierOnOff(self, state=None):
        """Get or set the on/off state of the CW signal"""
        if state is not None:
            command = self.CarrierOnOffSetStr(state)
            yield self.write(command)
            self.marDict['on_off'] = state
        returnValue(self.marDict['on_off'])

    @inlineCallbacks
    def requestRF(self):
        """requests the RF status"""
        result = yield self.query('RFLV?')
        if 'ON' in result:
            answer=True
        else:
            answer=False
        returnValue(answer)

    @inlineCallbacks
    def setAmplitude(self, level):
        """Sets power level, enter power in dBm"""
        if not self.marDict['power_min'] <= level <= self.marDict['power_max']:
            raise Exception("power out of bounds")
        command = self.PowerSetStr(level)
        print command
        yield self.write(command)
        self.marDict['power'] = level
        returnValue(self.marDict['power'])
        
    @inlineCallbacks
    def getAmplitude(self):
         "Gets the Amplitude in dbm"
         power = yield self.query('RFLV:VALUE?')
         power = float(power)
         returnValue(power)

    @inlineCallbacks
    def setFrequency(self, freq):
        if not self.marDict['freq_min'] <= freq['MHz'] <= self.marDict['freq_max']:
            raise Exception("Frequency out of bounds")
        yield self.write('CFRQ:Value {}MHZ'.format(freq['MHz']))
        print freq
        self.marDict['freq']=freq

    @inlineCallbacks
    def getFrequency(self):
        """Get the CW frequency (MHz)"""
        freq = yield self.query('CFRQ:VALUE?')
        freq = float(freq)
        freq = WithUnit(freq, 'Hz')
        returnValue(freq)

    # ===== SWEEP =====

    @inlineCallbacks
    def _CarrierMode(self, mode=None):
        """Get or set the carrier mode to 'FIXED' or 'SWEPT' """
        if mode is not None:
            if mode not in ('FIXED', 'SWEPT'):
                raise ValueError("Carrier mode must be 'FIXED', or 'SWEPT'")
            command = self.CarrierModeSetStr(mode)
            yield self.write(command)
            self.marDict['carrier_mode'] = mode
        returnValue(self.marDict['carrier_mode'])
    
    @inlineCallbacks
    def _SweepRangeStart(self, start=None):
        """Get or set the starting point for carrier frequency sweeps (MHZ)."""
        if start is not None:
            start = start['MHz']
            checkedStart = self.checkFreq(start)
            command = self.SweepStartSetStr(checkedStart)
            yield self.write(command)
            self.marDict['sweep_range_start'] = checkedStart
        value = self.marDict['sweep_range_start']
        returnValue(WithUnit(value,'MHz'))

    @inlineCallbacks
    def _SweepRangeStop(self, stop=None):
        """Get or set the stoping point for carrier frequency sweeps (MHZ)."""
        if stop is not None:
            checkedStop = self.checkFreq(stop)
            command = self.SweepStartSetStr(checkedStop)
            yield self.write(command)
            self.marDict['sweep_range_stop'] = checkedStop
        returnValue(self.marDict['sweep_range_stop'])

    @inlineCallbacks
    def _SweepStep(self, step=None):
        """Get or set the sweep step (MHz)"""
        if step is not None:
            command = self.SweepStepSetStr(step)
            yield self.write(command)
            self.marDict['sweep_step'] = step
        returnValue(self.marDict['sweep_step'])

    @inlineCallbacks
    def _SweepTime(self, time=None):
        """Get or set the time to complete one sweep step (ms)"""
        if time is not None:
            command = self.SweepTimeSetStr(time)
            yield self.write(command)
            self.marDict['sweep_time'] = time
        returnValue(self.marDict['sweep_time'])

    @inlineCallbacks
    def _SweepMode(self, mode=None):
        """Get or set the sweep mode to single (SNGL) or continuous (CONT)"""
        if mode is not None:
            command = self.SweepModeSetStr(mode)
            yield self.write(command)
            self.marDict['sweep_mode'] = mode
        returnValue(self.marDict['sweep_mode'])

    @inlineCallbacks
    def _SweepShape(self, shape=None):
        """Get or set the sweep shape to linear (LIN) of log (LOG)"""
        if shape is not None:
            command = self.SweepShapeSetStr(shape)
            yield self.write(command)
            self.marDict['sweep_shape'] = shape
        returnValue(self.marDict['sweep_shape'])

    @inlineCallbacks
    def _SweepTrigMode(self, trig_mode=None):
        """Get or set the external trigger mode.
        Options are: OFF, START, STARTSTOP, STEP"""
        if trig_mode is not None:
            command = self.SweepTrigModeSetStr(trig_mode)
            yield self.write(command)
            self.marDict['trig_mode'] = trig_mode
        returnValue(self.marDict['trig_mode'])

    def checkCarrierMode(self):
        """Throws a CarrierModeException if the carrier mode is not 'SWEPT'.
        Carrier mode must be swept before other sweep methods asetFrequencyre used."""
        if self.marDict['carrier_mode'] != 'SWEPT':
            raise Exception("Carrier mode is not 'SWEPT'")

    @inlineCallbacks
    def _SweepBegin(self):
        """Start a sweep"""
        self.checkCarrierMode()
        command = self.SweepBeginStr()
        yield self.write(command)

    @inlineCallbacks
    def _SweepPause(self):
        """Pause the current sweep"""
        self.checkCarrierMode()
        command = self.SweepPauseStr()
        yield self.write(command)

    @inlineCallbacks
    def _SweepContinue(self):
        """Continue the currently paused sweep"""
        self.checkCarrierMode()
        command = self.SweepContinueStr()
        yield self.write(command)

    @inlineCallbacks
    def _SweepReset(self):
        """Reset the current sweep to the start frequency"""
        self.checkCarrierMode()
        command = self.SweepResetStr()
        yield self.write(command)


    # ++++++++++++++++++++++++++++++++
    # ===== MARCONI STR MESSAGES =====
    # ++++++++++++++++++++++++++++++++        

    # ===== BASIC =====
    
    def IdenStr(self):
        """String to request machine to identify itself"""
        return '*IDN?' + '\n'

    def CarrierOnOffReqStr(self):
        """String to request carrier on/off state"""
        return 'RFLV?' + '\n'

    def CarrierOnOffSetStr(self, state):
        """String to set carrier state on/off. True (ON) or False (OFF)"""
        if state:
            return 'RFLV:ON' + '\n'
        else:
            return 'RFLV:OFF' + '\n'
     
    def PowerReqStr(self):
        """String to request current power"""
        return 'RFLV?' + '\n'

    def PowerSetStr(self, pwr):
        """String to set power (in dBm)"""
        return 'RFLV:Value {} DBM\n'.format(pwr['dBm'])


    # ===== SWEEP =====setFrequency
    
    def CarrierModeSetStr(self, mode):
        """String to set carrier to FIXED or SWEPT mode"""
        mode = mode.upper()
        if not mode in ('FIXED', 'SWEPT'):
            raise ValueError("Carrier mode is 'FIXED' or 'SWEPT'")
        return 'CFRQ:MODE ' + mode + '\n'

    def SweepStartSetStr(self, start):
        """String to set starting frequency for carrier sweep (MHZ)"""
        return 'SWEEP:START ' + str(start) + ' MHZ' + '\n'

    def SweepStopSetStr(self, stop):
        """String to set stopping frequency for carrier sweep (MHZ)"""
        return 'SWEEP:STOP ' + str(stop) + ' MHZ' + '\n'

    def SweepStepSetStr(self, step):
        """String to set frequency step size for carrier sweep (KHZ)"""
        return 'SWEEP:INC ' + str(step) + ' KHZ' + '\n'

    def SweepTimeSetStr(self, time):
        """String to set time to complete a step of carrier sweep (S)"""
        return 'SWEEP:TIME ' + str(time) + ' MS' + '\n'

    def SweepModeSetStr(self, mode):
        """String to set sweep mode to SNGL shot or CONT sweep"""
        mode = mode.upper()
        if not mode in ('SNGL', 'CONT'):
            raise ValueError("Sweep mode is 'SNGL' or 'CONT'")
        return 'SWEEP:MODE ' + mode + '\n'

    def SweepShapeSetStr(self, shape):
        """String to set shape of sweep to linear (LIN) or logarithmic (LOG)"""
        shape = shape.upper()
        if not shape in ('LIN', 'LOG'):
            raise ValueError("Sweep shape is 'LIN' or 'LOG'")
        return 'SWEEP:TYPE ' + shape + '\n'

    def SweepTrigModeSetStr(self, trig_mode):
        """String to set trigger mode to OFF, START, STARTSTOP, or STEP
        as described in the Marconi Manual"""
        trig_mode = trig_mode.upper()
        if not trig_mode in ('setFrequencyOFF', 'START', 'STARTSTOP', 'STEP'):
            raise ValueError("Sweep trigger mode must be one of: "\
                            "'OFF', 'STAfrequencyRT', 'STARTSTOP', or 'STEP'")
        return 'SWEEP:TRIG ' + trig_mode + '\n'

    def SweepBeginStr(self):
        """String to begin sweeping"""
        return 'SWEEP:GO' + '\n'

    def SweepPauseStr(self):
        """String to pause sweeping (at current location in sweep)"""
        return 'SWEEP:HALT' + '\n'

    def SweepContinueStr(self):
        """String to continue sweeping (from pause point)"""
        return 'SWEEP:CONT' + '\n'

    def SweepResetStr(self):
        """String to reset sweeping point to start"""
        return 'SWEEP:RESET' + '\n'



class MarconiServer(GPIBManagedServer):
    """Provides basic CW control for Marconi 2024 RF Generators"""
    name = 'Marconi Server'
    deviceName = 'IFR 2024'
    deviceWrapper = Marconi2024Wrapper


    # +++++++++++++++++++++++++
    # ===== META SETTINGS =====frequency
    # +++++++++++++++++++++++++

    @setting(14, "Save Settings", saveName='s', returns='')
    def SaveSettings(self, c, saveName='MostRecentSettings'):
        """Save the current server settings in the registry under 'saveName'
        or 'MostRecentSettings' if saveName is unspecified."""
        yield self._SaveSettings(saveName)

    @setting(15, "Load Settings", loadName='s', returns='b')
    def LoadSettings(self, c, loadName='MostRecentSettings'):
        """Load previous server settings. If loadName is unspecified, loads from
        'MostRecentSettings' otherwise loads from loadName."""
        yield self._LoadSettinsetFrequencygs(loadName)


    # +++++++++++++++++++++++++++
    # ===== BASIC SETTINGS ======
    # +++++++++++++++++++++++++++

    @setting(10, "Identify", returns = 's')
    def Identify(self, c):
        """Ask instrument to identify itself"""
        dev=self.selectDevice(c)
        return dev._Identify()

    @setting(11, "OnOff", state = 'b', returns = 'b')
    def CarrierOnOff(self, c, state=None):
        """Get or set the on/off state of the CW signal.
        True represents ON
        False represents OFF"""
        dev=self.selectDevice(c)
        return dev._CarrierOnOff(state)

    @setting(12, "Amplitude", level = 'v[dBm]', returns = "v[dBm]")
    def Amplitude(self, c, level=None):
        """Get or set the power level (dBm)"""
        dev = self.selectDevice(c)
        if level is not None:
            yield dev.setAmplitude(level)
        returnValue(dev.amplitude)
    
    @setting(13, "Frequency", freq = 'v[MHz]', returns='v[MHz]')
    def Frequency(self, c, freq=None):
        """Get or set the CW frequency (MHz)"""
        dev = self.selectDevice(c)
        if freq is not None:
            yield dev.setFrequency(freq)
        returnValue(dev.frequency)


    # ++++++++++++++++++++++++++++
    # ===== SWEEP SETTINGS ======
    # ++++++++++++++++++++++++++++

    @setting(20, "Carrier Mode", mode = 's', returns = 's') # or 's'
    def CarrierMode(self, c, mode=None):
        """Get or set the carrier mode to 'FIXED' or 'SWEPT' """
        dev=self.selectDevice(c)
        return dev._CarrierMode(mode)

    @setting(21, "Sweep Range Start", start = 'v[MHz]', returns = 'v[MHz]')
    def SweepRangeStart(self, c, start=None):
        """Get or set the starting frequency for carrier frequency sweeps (MHZ)"""
        dev=self.selectDevice(c)
        return dev._SweepRangeStart(start)

    @setting(22, "Sweep Range Stop", stop = 'v[MHz]', returns = 'v[MHz]')
    def SweepRangeStop(self, c, stop=None):
        """Get or set the ending frequency for carrier frequency sweeps (MHZ)"""
        dev=self.selectDevice(c)
        return dev._SweepRangeStop(stop)

    @setting(23, "Sweep Step", step = 'v', returns = 'v')
    def SweepStep(self, c, step=None):
        """Get or set the size of the sweep step (MHZ)"""
        dev=self.selectDevice(c)
        return dev._SweepStep(step)

    @setting(24, "Sweep Time", time = 'v', returns = 'v')
    def SweepTime(self, c, time=None):
        """Get or set the time to complete one sweep step (ms)"""
        dev=self.selectDevice(c)
        return dev._SweepTime(time)

    @setting(25, "Sweep Mode", mode = 's', returns = 's')
    def SweepMode(self, c, mode=None):
        """Get or set the sweep mode to single shot ('SNGL') or continuous ('CONT')"""
        dev=self.selectDevice(c)
        return dev._SweepMode(mode)

    @setting(26, "Sweep Shape", shape = 's', returns = 's')
    def SweepShape(self, c, shape=None):
        """Get or set the sweep shape to linear ('LIN') of log ('LOG')"""
        dev=self.selectDevice(c)
        return dev._SweepShape(shape)

    @setting(27, "Sweep Trig Mode", trig_mode = 's', returns = 's')
    def SweepTrigMode(self, c, trig_mode=None):
        """Get or set the external trigger mode.
        Options are: OFF, START, STARTSTOP, STEP.
        (See Marconi manual for details."""
        dev=self.selectDevice(c)
        return dev._SweepTrigMode(trig_mode)

    @setting(30, "Sweep Begin", returns = '')
    def SweepBegin(self, c):
        """Start a sweep"""
        dev=self.selectDevice(c)
        return dev._SweepBegin()

    @setting(31, "Sweep Pause", returns = '')
    def SweepPause(self, c):
        """Pause the current sweep"""
        dev=self.selectDevice(c)
        return dev._SweepPause()

    @setting(32, "Sweep Continue", returns = '')
    def SweepContinue(self, c):
        """Continue a currently paused sweep"""
        dev=self.selectDevice(c)
        return dev._SweepContinue()

    @setting(33, "Sweep Reset", returns = '')
    def SweepReset(self, c):
        """Reset the current sweep to the start frequency"""
        dev=self.selectDevice(c)
        return dev._SweepReset()
        
__server__ = MarconiServer()

if __name__ == '__main__':
    print 'here'
    from labrad import util
    util.runServer(__server__)
    s = __server__
#    print 'Frequency = ' + str(s.frequency)
#    print 'Amplitude = ' + str(s.amplitude)
#    print 'Output State = ' + s.output
