from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks

# Constants that set the behavior of various UI buttons
# and spin boxes.
FREQ_MIN = 0.009        # 9 KHz     minimum settable frequency
FREQ_MAX = 2400         # 2400 MHz  maximum settable frequency
SWEEP_RANGE_STEP = 0.05 # 50 kHz    step of single click of sweep range spin box
SWEEP_STEP_STEP = 1     # 1 kHz     step of single click of sweep step spin box
STEP_MIN = 0.001        # 1 Hz      minimum settable frequency step
STEP_MAX = 1000         # 1 MHz     maximum settable frequency step
SWEEP_TIME_STEP = 5     # 10 ms     step of single click of sweep time spin box
TIME_MIN = 20           # 20 ms     mimimum settable time/step
TIME_MAX = 100000       # 100 sec   maximum settable time/step

class SWEEP_WIDGET(QtGui.QWidget):
    """
    Widget for interfacing with the sweep functionality of a signal generator.
    
    This must be embedded in (another) application's main window, for example
    the SWEEP_CONTROL class defined below.
    
    """
    def __init__(self, reactor, parent=None):
        super(SWEEP_WIDGET, self).__init__(parent)
        self.reactor = reactor
        self.makeGui()
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Connect to LabRAD and load server settings."""
        from labrad.wrappers import connectAsync

        self.cxn = yield connectAsync()                     # '192.168.169.30'
        try:
            self.server = yield self.cxn.marconi_server
            self.update()
        except AttributeError:
            print "Need to start Marconi Server"
            self.setEnabled(False)
        
        ## If have more than one marconi connecting to marconi server
        ## it may be necessary to specify the serial port or GPIB
        ## address of the device you wish to connect to.
        ## Implement latter if necessary.


    def makeGui(self):
        """Create and array widgets in a main layout."""
        mainLayout = QtGui.QGridLayout()
        groupbox = QtGui.QGroupBox('Sweep Control (Marconi)')
        groupboxLayout = QtGui.QGridLayout()

        # topLayout
        topLayout = QtGui.QGridLayout()
        self.carrierModeButton = self.makeCarrierModeButton()
        self.sweepTrigModeToggle = self.makeSweepTrigModeToggle()
        topLayout.addWidget(QtGui.QLabel("Carrier Mode"), 0, 0)
        topLayout.addWidget(self.carrierModeButton, 0, 1)
        topLayout.addWidget(QtGui.QLabel("Tigger Mode"), 1, 0)
        topLayout.addWidget(self.sweepTrigModeToggle, 1, 1)

        # upperMiddleLayout
        upperMiddleLayout = QtGui.QGridLayout()
        self.sweepRangeStartCtrl = self.makeSweepRangeStartCtrl()
        self.sweepRangeStopCtrl = self.makeSweepRangeStopCtrl()
        upperMiddleLayout.addWidget(QtGui.QLabel("Start Frequency (MHz)"), 0, 0)
        upperMiddleLayout.addWidget(self.sweepRangeStartCtrl, 0, 1)
        upperMiddleLayout.addWidget(QtGui.QLabel("Stop Frequency (MHz)"), 1, 0)
        upperMiddleLayout.addWidget(self.sweepRangeStopCtrl, 1, 1)

        # lowerMiddleLayout
        lowerMiddleLayout = QtGui.QGridLayout()
        self.sweepStepCtrl = self.makeSweepStepCtrl()
        self.sweepTimeCtrl = self.makeSweepTimeCtrl()
        lowerMiddleLayout.addWidget(QtGui.QLabel("Step Size (KHz)"), 0, 0)
        lowerMiddleLayout.addWidget(self.sweepStepCtrl, 0, 1)
        lowerMiddleLayout.addWidget(QtGui.QLabel("Time/Step (ms)"), 1, 0)
        lowerMiddleLayout.addWidget(self.sweepTimeCtrl, 1, 1)

        # bottomLayout
        bottomLayout = QtGui.QGridLayout()
        self.sweepBeginButton = self.makeSweepBeginButton()
        self.sweepPauseButton = self.makeSweepPauseButton()
        self.sweepContinueButton = self.makeSweepContinueButton()
        self.sweepResetButton = self.makeSweepResetButton()
        self.sweepUpdateButton = self.makeUpdateButton()
        bottomLayout.addWidget(self.sweepBeginButton, 0, 0)
        bottomLayout.addWidget(self.sweepPauseButton, 1, 0)
        bottomLayout.addWidget(self.sweepContinueButton, 1, 1)
        bottomLayout.addWidget(self.sweepResetButton, 0, 1)
        bottomLayout.addWidget(self.sweepUpdateButton, 2, 0, 1, 2)

        # order layouts in the groupboxLayout
        groupboxLayout.addLayout(topLayout, 0, 0)
        groupboxLayout.addLayout(upperMiddleLayout, 1, 0)
        groupboxLayout.addLayout(lowerMiddleLayout, 2, 0)
        groupboxLayout.addLayout(bottomLayout, 3, 0)
        
        # everything goes in the mainLayout
        groupbox.setLayout(groupboxLayout) # set the groupboxLayout in the groupbox
        mainLayout.addWidget(groupbox) # put the groupbox in the mainLayout
        self.setLayout(mainLayout) # set this widget's main layout


    @inlineCallbacks
    def update(self, unused=None):  # parameter unused is not used
        """Updates values of controls based on server's records"""
        CarrierModeState = yield self.server.carrier_mode()
        if CarrierModeState == "FIXED":
            self.carrierModeButton.setText("FIXED")
        elif CarrierModeState == "SWEPT":
            self.carrierModeButton.setText("SWEPT")

        trig = yield self.server.sweep_trig_mode()
        self.sweepTrigModeToggle.setText(trig)
        
        start = yield self.server.sweep_range_start()
        stop = yield self.server.sweep_range_stop()
        step = yield self.server.sweep_step()
        time = yield self.server.sweep_time()

        self.sweepRangeStartCtrl.setValue(start)
        self.sweepRangeStopCtrl.setValue(stop)
        self.sweepStepCtrl.setValue(step)
        self.sweepTimeCtrl.setValue(time)


    # +++++++++++++++++++++++++++++++++
    # ===== MAKE CONTROLS/BUTTONS =====
    # +++++++++++++++++++++++++++++++++


    def makeCarrierModeButton(self):
        """Button for switching between 'FIXED' and 'SWEPT' carrier mode."""
        carrierModeButton = QtGui.QPushButton()
        carrierModeButton.setText('Carrier Mode, Unknown')
        
        @inlineCallbacks
        def onCarrierModeChange(unused): # parameter unused is not used
            """Toggle carrier mode."""
            mode = yield self.server.carrier_mode()
            if mode == 'SWEPT':
                # changing to FIXED
                carrierModeButton.setText('FIXED')
                yield self.server.carrier_mode('FIXED')
            else:
                # changing to SWEPT
                carrierModeButton.setText('SWEPT')
                yield self.server.carrier_mode('SWEPT')

        carrierModeButton.clicked.connect(onCarrierModeChange)
        return carrierModeButton

    def makeSweepTrigModeToggle(self):
        """Button to toggle through triggering mode options.

        Options are: OFF, START, STARTSTOP, STEP. See Marconi Manual for 
        details on what each of these settings means.
        
        """
        sweepTrigModeToggle = QtGui.QPushButton()
        sweepTrigModeToggle.setText("Trig Mode, Unknown")

        @inlineCallbacks
        def onSweepTrigModeChange(unused):
            """Toggle trigger mode."""
            mode = yield self.server.sweep_trig_mode()
            if mode == 'OFF':
                sweepTrigModeToggle.setText('START')
                yield self.server.sweep_trig_mode('START')
            elif mode == 'START':
                sweepTrigModeToggle.setText('STARTSTOP')
                yield self.server.sweep_trig_mode('STARTSTOP')
            elif mode == 'STARTSTOP':
                sweepTrigModeToggle.setText('STEP')
                yield self.server.sweep_trig_mode('STEP')
            elif mode == 'STEP':
                sweepTrigModeToggle.setText('OFF')
                yield self.server.sweep_trig_mode('OFF')

        sweepTrigModeToggle.clicked.connect(onSweepTrigModeChange)
        return sweepTrigModeToggle

    def makeSweepRangeStartCtrl(self):
        """Control the starting frequency of sweeps."""
        sweepRangeStartCtrl = QtGui.QDoubleSpinBox()
        sweepRangeStartCtrl.setRange(FREQ_MIN, FREQ_MAX)
        sweepRangeStartCtrl.setDecimals(5)
        sweepRangeStartCtrl.setSingleStep(SWEEP_RANGE_STEP)

        @inlineCallbacks
        def onSweepRangeStartChange(start):
            yield self.server.sweep_range_start(start)

        sweepRangeStartCtrl.valueChanged.connect(onSweepRangeStartChange)
        return sweepRangeStartCtrl

    def makeSweepRangeStopCtrl(self):
        """Control the stoping frequency of sweeps."""
        sweepRangeStopCtrl = QtGui.QDoubleSpinBox()
        sweepRangeStopCtrl.setRange(FREQ_MIN, FREQ_MAX)
        sweepRangeStopCtrl.setDecimals(5)
        sweepRangeStopCtrl.setSingleStep(SWEEP_RANGE_STEP)

        @inlineCallbacks
        def onSweepRangeStopChange(stop):
            yield self.server.sweep_range_stop(stop)

        sweepRangeStopCtrl.valueChanged.connect(onSweepRangeStopChange)
        return sweepRangeStopCtrl

    def makeSweepStepCtrl(self):
        """Control the frequency step of the sweep."""
        sweepStepCtrl = QtGui.QDoubleSpinBox()
        sweepStepCtrl.setRange(STEP_MIN, STEP_MAX)
        sweepStepCtrl.setDecimals(1)
        sweepStepCtrl.setSingleStep(SWEEP_STEP_STEP)

        @inlineCallbacks
        def onSweepStepCtrlChange(step):
            yield self.server.sweep_step(step)

        sweepStepCtrl.valueChanged.connect(onSweepStepCtrlChange)
        return sweepStepCtrl

    def makeSweepTimeCtrl(self):
        """Control the time between steps for sweeping."""
        sweepTimeCtrl = QtGui.QDoubleSpinBox()
        sweepTimeCtrl.setRange(TIME_MIN, TIME_MAX)
        sweepTimeCtrl.setDecimals(1)
        sweepTimeCtrl.setSingleStep(SWEEP_TIME_STEP)

        @inlineCallbacks
        def onSweepTimeCtrlChange(time):
            yield self.server.sweep_time(time)

        sweepTimeCtrl.valueChanged.connect(onSweepTimeCtrlChange)
        return sweepTimeCtrl

    def makeSweepBeginButton(self):
        """Button to start a sweep (manual trigger)."""
        sweepBeginButton = QtGui.QPushButton()
        sweepBeginButton.setText("Start")

        @inlineCallbacks
        def onSweepBeginButtonChange(_):
            yield self.server.sweep_begin()
        
        sweepBeginButton.clicked.connect(onSweepBeginButtonChange)
        return sweepBeginButton

    def makeSweepPauseButton(self):
        """Button to pause a sweep."""
        sweepPauseButton = QtGui.QPushButton()
        sweepPauseButton.setText("Pause")

        @inlineCallbacks
        def onSweepPauseButton(_):
            yield self.server.sweep_pause()

        sweepPauseButton.clicked.connect(onSweepPauseButton)
        return sweepPauseButton

    def makeSweepContinueButton(self):
        """Button to continue a paused sweep."""
        sweepContinueButton = QtGui.QPushButton()
        sweepContinueButton.setText("Continue")

        @inlineCallbacks
        def onSweepContinueButton(_):
            yield self.server.sweep_continue()

        sweepContinueButton.clicked.connect(onSweepContinueButton)
        return sweepContinueButton

    def makeSweepResetButton(self):
        """Button to reset the sweep frequency to the start value."""
        sweepResetButton = QtGui.QPushButton()
        sweepResetButton.setText("Reset")

        @inlineCallbacks
        def onSweepResetButton(_):
            yield self.server.sweep_reset()

        sweepResetButton.clicked.connect(onSweepResetButton)
        return sweepResetButton

    def makeUpdateButton(self):
        """Button to reload server settings (in case of mismatch)."""
        sweepUpdateButton = QtGui.QPushButton()
        sweepUpdateButton.setText("Get")
        sweepUpdateButton.clicked.connect(self.update)
        return sweepUpdateButton


class SWEEP_CONTROL(QtGui.QMainWindow):
    """
    A main window providing a widget that gives access to the 
    sweep functionality of a function generator server. This can
    be run as an independent application.
    
    """

    def __init__(self, reactor, parent=None):
        super(SWEEP_CONTROL, self).__init__(parent)
        self.reactor = reactor

        sweepWidget = SWEEP_WIDGET(self.reactor)
        self.setCentralWidget(sweepWidget)
        self.setWindowTitle('Sweep Control (Marconi)')

    def closeEvent(self, unused):   # parameter unused is not used
        self.reactor.stop()


if __name__ == "__main__":
    # start a SWEEP_CONTROL as an independent application
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    sweepUI = SWEEP_CONTROL(reactor)
    sweepUI.show()
    reactor.run()
