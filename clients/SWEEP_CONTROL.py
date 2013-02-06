import os

from PsQt3 import QtGui
from twisted.internet.defer import inlineCallbacks, returnValue

from labrad.wrapper import connectAsync
from labrad.types import Error
from labrad import types as T                                   ## obfuscation

FREQ_MIN
FREQ_MAX
SWEEP_RANGE_STEP = 0.05
SWEEP_STEP_STEP = 0.0
SWEEP_TIME_STEP


class SWEEP_WIDGET(QTGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(SWEEP_WIDGET, self).__init__(parent)
        self.reactor = reactor
        self.connect()
        self.makeGui()

    def makeGui():
        mainLayout = QtGui.QGridLayout()
        groupbox = QtGui.QGroupBox('Sweep Control (Marconi)')
        groupboxLayout = QtGui.QGridLayout()

        # build controls and put in sublayouts
        # topLayout
        self.carrierModeButton = QtQui.QPushButton() # change FIXED or SWEPT
        self.sweepTrigModeToggle = QtGui.QPushButton     # make it a menu button 
        #needs a menu
        topLayout = QtGui.QGridLayout()
        topLayout.addWidget(self.carrierModeButton, 0, 0)
        topLayout.addWidget(self.sweepTrigModeToggle, 0, 1)

        # upperMiddleLayout
        self.sweepRangeStartCtrl = QtGui.QDoubleSpinBox() # change sweep start freq
        #self.sweepRangeStartCtrl.setRange()
        self.sweepRangeStartCtrl.setDecimals(5)
        self.sweepRangeStartCtrl.setSingleStep(SWEEP_RANGE_STEP)
        self.sweepRangeStopCtrl = QtGui.QDoubleSpinBox() # change sweep stop freq
        #self.sweepRangeStartCtrl.setRange()
        self.sweepRangeStopCtrl.setDecimals(5)
        self.sweepRangeStopCtrl.setSingleStep(SWEEP_RANGE_STEP)
        upperMiddleLayout = QtGui.QGridLayout()
        upperMiddleLayout.addWidget(self.sweepRangeStartCtrl, 0, 0)
        upperMiddleLayout.addWidget(self.sweepRangeStopCtrl, 0, 1)
        
        # lowerMiddleLayout
        self.sweepStepCtrl = QtGui.QDoubleSpinBox()      # change sweep step
        #self.sweepStepCtrl.setRange(
        self.sweepStepCtrl.setDecimals(5)
        self.sweepStepCtrl.setSingleStep(SWEEP_STEP_STEP)
        self.sweepTimeCtrl = QtGui.QDoubleSpinBox()      # change sweep time/step
        #self.sweepTimeCtrl.setRange(
        self.sweepTimeCtrl.setDecimals(1)
        self.sweepTimeCtrl.setSingleStep(SWEEP_TIME_STEP)
        lowerMiddleLayout = QtGui.QGridLayout()
        lowerMiddleLayout.addWidget(QtGui.QLabel('Sweep Step [MHz]'), 0, 0)
        lowerMiddleLayout.addWidget(self.sweepStepCtrl, 1, 0)
        lowerMiddleLayout.addWidget(QtGui.QLabel('Time/Step [ms]'), 0, 1)
        lowerMiddleLayout.addWidget(self.sweepTimeCtrl, 1, 1)

        # bottomLayout
        self.sweepBeginButton = QtGui.QPushButton()      # start a sweep
        self.sweepPauseButton = QtGui.QPushButton()      # pause the sweep
        self.sweepContinueButton = QtGui.QPushBotton()   # continue after pause
        self.sweepResetButton = QtGui.QPushButton()      # reset the sweep freq
        bottomLayout = QtGui.QGridLayout()
        bottomLayout.addWidget(sweepBeginButton)
        bottomLayout.addWidget(sweepPauseButton)
        bottomLayout.addWidget(sweepContinueButton)
        bottomLayout.addWidget(sweepResetButton)

        # add them to the groupboxLayout
        groupboxLayout.addLayout(topLayout)
        groupboxLayout.addLayout(upperMiddleLayout)
        groupboxLayout.addLayout(lowerMiddleLayout)
        groupboxLayout.addLayout(bottomLayout)
        
        # everything goes in the mainLayout
        groupbox.setLayout(groupboxLayout) # set the groupboxLayout in the groupbox
        mainLayout.addWidget(groupbox) # put the groupbox in the mainLayout
        self.setLayout(mainLayout) # set this widget's main layout

    def connect():
        self.cxn = yield connectAsync()                     # '192.168.169.30'
        self.server = yield self.cxn.marconi_server
        
        ## if have more than one marconi connecting to marconi server
        ## it may be necessary to specify the serial port or GPIB
        ## address. implement latter if necessary.

        self.update(0)                                      # what is 0 for?
        # define all onChange methods and give them to valueChanged
        # for example:
        # self.powerCtrl.valueChaned.connect(self.onPowerChange)
        #
        # ...


class SWEEP_CONTROL(QTGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(SWEEP_CONTROL, self).__init__(parent)
        self.reactor = reactor

        sweepWidget = SWEEP_WIDGET(self.reactor)
        #self.setWindowTitle('Sweep Control (Marconi)')
        self.setCentralWidget(sweepWidget)

    def closeEvent(self, x):
        self.reactor.stop()

def main():                                                 # necessary?
    import qt4reactor
    from twisted.internet import reactor
    app = QtQui.QApplication( [] )
    qt4reactor.install()
    sweepUI = SWEEP_CONTROL(reactor)
    sweepUI.show()
    reactor.run()

if __name__ == "__main__":
    main()
