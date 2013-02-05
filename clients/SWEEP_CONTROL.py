import os

from PsQt3 import QtGui
from PyQt4 import QtCore
from twisted.internet.defer import inlineCallbacks, returnValue

from labrad.wrapper import connectAsync
from labrad.types import Error
from labrad import types as T                                   ## obfuscation


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

        # build controls
        # ...
        carrierModeButton = QtQui.QPushButton() # change FIXED or SWEPT
        sweepRangeStartCtrl = QtGui.QDoubleSpinBox() # change sweep start freq
        sweepRangeStopCtrl = QtGui.QDoubleSpinBox() # change sweep stop freq
        sweepStepCtrl = QtGui.QDoubleSpinBox()      # change sweep step
        sweepTimeCtrl = QtGui.QDoubleSpinBox()      # change sweep time/step
        #sweepTrigModeToggle    # make a button that toggles 4 values
        sweepBeginButton = QtGui.QPushButton()      # start a sweep
        sweepPauseButton = QtGui.QPushButton()      # pause the sweep
        sweepContinueButton = QtGui.QPushBotton()   # continue after pause
        sweepResetButton = QtGui.QPushButton()      # reset the sweep freq
        
        # NOTE: QtGui.QGridLayout has an addLayout method, so you can
        # have a hierarchical organization to make things go where you want

        # add them to the groupboxLayout
        # ...
        # groupboxLayout.addWidget(ctrl, 0, 0) ...

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
