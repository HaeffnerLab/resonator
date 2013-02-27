from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks

FREQ_MIN = 0.009        # 9 KHz
FREQ_MAX = 2400         # 2400 MHz
SWEEP_RANGE_STEP = 0.05 # 50 kHz
SWEEP_STEP_STEP = 0.1   # 100 Hz
STEP_MIN = 0.001        # 1 Hz
STEP_MAX = 1000         # 1 MHz
SWEEP_TIME_STEP = 5     # 10 ms
TIME_MIN = 20           # 20 ms
TIME_MAX = 100000       # 100 sec


class SWEEP_WIDGET(QtGui.QWidget):
    '''Blueprint for a widget that interfaces with the sweep functionality
    of a signal generator.'''

    def __init__(self, reactor, parent=None):
        super(SWEEP_WIDGET, self).__init__(parent)
        self.reactor = reactor
        self.connect()
        self.makeGui()
        self.update()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync

        self.cxn = yield connectAsync()                     # '192.168.169.30'
        self.server = yield self.cxn.marconi_server
        
        ## if have more than one marconi connecting to marconi server
        ## it may be necessary to specify the serial port or GPIB
        ## address. implement latter if necessary.


    def makeGui(self):
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
        bottomLayout.addWidget(self.sweepBeginButton, 0, 0)
        bottomLayout.addWidget(self.sweepPauseButton, 1, 0)
        bottomLayout.addWidget(self.sweepContinueButton, 1, 1)
        bottomLayout.addWidget(self.sweepResetButton, 0, 1)

        # order layouts in the groupboxLayout
        groupboxLayout.addLayout(topLayout, 0, 0)
        groupboxLayout.addLayout(upperMiddleLayout, 1, 0)
        groupboxLayout.addLayout(lowerMiddleLayout, 2, 0)
        groupboxLayout.addLayout(bottomLayout, 3, 0)
        
        # everything goes in the mainLayout
        groupbox.setLayout(groupboxLayout) # set the groupboxLayout in the groupbox
        mainLayout.addWidget(groupbox) # put the groupbox in the mainLayout
        self.setLayout(mainLayout) # set this widget's main layout


    #@inlineCallbacks
    def update(self):
        '''Sets the initial values of controls based on server's records'''
        # Should assume everything is FIXED to begin with

        # == LEFT OUT FOR TESTING ==
        #CarrierModeState = self.server.CarrierMode()
        #if CarrierModeState == "FIXED":
            #self.carrierModeButton.state = "FIXED"
        #elif CarrierModeState == "SWEPT":
            #state = False
        #else:
            #raise ValueError("Carrier mode not defined")
        #self.sweepTrigModeToggle.setValue(...) # query server and convert ans
        #self.sweepRangeStartCtrl.setValue(self.server.SweepRangeStart())
        #self.sweepRangeStopCtrl.setValue(self.server.SweepRangeStop())
        #self.sweepStepCtrl.setValue(self.server.SweepStep())
        #self.sweepTimeCtrl.setValue(self.server.SweepTime())
        pass


    # +++++++++++++++++++++++++++++++++
    # ===== MAKE CONTROLS/BUTTONS =====
    # +++++++++++++++++++++++++++++++++


    def makeCarrierModeButton(self):
        carrierModeButton = QtGui.QPushButton()
        carrierModeButton.setText('FIXED')
        carrierModeButton.state = 'FIXED'
        
        @inlineCallbacks
        def onCarrierModeChange(state): # does this need other parameters?
            print "CarrierMode state is: ", state
            if carrierModeButton.state == 'SWEPT':
                carrierModeButton.setText('FIXED') # set to fixed
                yield self.server.CarrierMode('FIXED')
                carrierModeButton.state = 'FIXED'
            else:
                carrierModeButton.setText('SWEPT') # set to swept
                yield self.server.CarrierMode('SWEPT')
                carrierModeButton.state = 'SWEPT'

        carrierModeButton.clicked.connect(onCarrierModeChange)
        return carrierModeButton


    def makeSweepTrigModeToggle(self):
        sweepTrigModeToggle = QtGui.QPushButton()
        # needs a menu

        @inlineCallbacks
        def onSweepTrigModeChange():
            pass

        return sweepTrigModeToggle


    def makeSweepRangeStartCtrl(self):
        sweepRangeStartCtrl = QtGui.QDoubleSpinBox()
        sweepRangeStartCtrl.setRange(FREQ_MIN, FREQ_MAX)
        sweepRangeStartCtrl.setDecimals(5)
        sweepRangeStartCtrl.setSingleStep(SWEEP_RANGE_STEP)

        @inlineCallbacks
        def onSweepRangeStartChange(start):
            try:
                yield self.server.SweepRangeStart(start) # could this be just value instead?
            except ValueError:
                # this might occur if one attempt to set start > stop freq
                stop = yield self.server.SweepRangeStop()
                sweepRangeStartCtrl.setValue(stop)

        sweepRangeStartCtrl.valueChanged.connect(onSweepRangeStartChange)
        return sweepRangeStartCtrl


    def makeSweepRangeStopCtrl(self):
        sweepRangeStopCtrl = QtGui.QDoubleSpinBox()
        sweepRangeStopCtrl.setRange(FREQ_MIN, FREQ_MAX)
        sweepRangeStopCtrl.setDecimals(5)
        sweepRangeStopCtrl.setSingleStep(SWEEP_RANGE_STEP)

        @inlineCallbacks
        def onSweepRangeStopChange(stop):
            try:
                yield self.server.SweepRangeStop(stop) # could this be just value instead?
            except ValuerError:
                # this might occur if one attempt to set stop < start freq
                stop = yield self.server.SweepRangeStop()
                sweepRangeStopCtrl.setValue(stop)

        sweepRangeStopCtrl.valueChanged.connect(onSweepRangeStopChange)
        return sweepRangeStopCtrl


    def makeSweepStepCtrl(self):
        sweepStepCtrl = QtGui.QDoubleSpinBox()
        sweepStepCtrl.setRange(TIME_MIN, TIME_MAX)
        sweepStepCtrl.setDecimals(1)
        sweepStepCtrl.setSingleStep(SWEEP_TIME_STEP)
        return sweepStepCtrl

    def makeSweepTimeCtrl(self):
        sweepTimeCtrl = QtGui.QDoubleSpinBox()
        sweepTimeCtrl.setRange(TIME_MIN, TIME_MAX)
        sweepTimeCtrl.setDecimals(1)
        sweepTimeCtrl.setSingleStep(SWEEP_STEP_STEP)
        return sweepTimeCtrl

    def makeSweepBeginButton(self):
        sweepBeginButton = QtGui.QPushButton()
        sweepBeginButton.setText("Start")
        return sweepBeginButton

    def makeSweepPauseButton(self):
        sweepPauseButton = QtGui.QPushButton()
        sweepPauseButton.setText("Pause")
        return sweepPauseButton

    def makeSweepContinueButton(self):
        sweepContinueButton = QtGui.QPushButton()
        sweepContinueButton.setText("Continue")
        return sweepContinueButton

    def makeSweepResetButton(self):
        sweepResetButton = QtGui.QPushButton()
        sweepResetButton.setText("Reset")
        return sweepResetButton


class SWEEP_CONTROL(QtGui.QMainWindow):
    '''A main window providing a widget that gives access to the 
    sweep functionality of a function generator server.'''

    def __init__(self, reactor, parent=None):
        super(SWEEP_CONTROL, self).__init__(parent)
        self.reactor = reactor

        sweepWidget = SWEEP_WIDGET(self.reactor)
        self.setCentralWidget(sweepWidget)
        self.setWindowTitle('Sweep Control (Marconi)')

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    sweepUI = SWEEP_CONTROL(reactor)
    sweepUI.show()
    reactor.run()
