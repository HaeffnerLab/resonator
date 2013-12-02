import os

from PyQt4 import QtGui
from PyQt4 import QtCore,uic
from twisted.internet.defer import inlineCallbacks, returnValue
from Devices_config import Device_config


MinPower = -36 #dbM
MaxPower = 25
DEFPower = -20
MinFreq = 0 #Mhz
MaxFreq = 100
DEFFreq = 10

class TD(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(TD,self).__init__(parent)
        self.reactor = reactor
        self.connect()
        self.makeGUI()
        
    def makeGUI(self):
        layout = QtGui.QGridLayout()
        subLayout = QtGui.QGridLayout()
        superLayout = QtGui.QGridLayout()
        groupbox = QtGui.QGroupBox('Trap Drive')
        groupboxLayout = QtGui.QGridLayout()
        self.powerCtrl = QtGui.QDoubleSpinBox()
        self.powerCtrl.setRange (MinPower,MaxPower)
        self.powerCtrl.setDecimals (2)
        self.powerCtrl.setSingleStep(.5)
#        self.powerCtrl.setSuffix(' dBm')
        self.frequencyCtrl = QtGui.QDoubleSpinBox()
        self.frequencyCtrl.setRange (MinFreq,MaxFreq)
        self.frequencyCtrl.setDecimals (5)
        self.frequencyCtrl.setSingleStep(.1)
#        self.frequencyCtrl.setSuffix(' MHz')
        self.updateButton = QtGui.QPushButton('Get')
        self.stateButton = QtGui.QPushButton()
        self.maximumButton = QtGui.QPushButton('Maximum')
        
        superLayout.addLayout(layout,0,0)
        groupbox.setLayout(groupboxLayout)
        layout.addWidget(groupbox,0,0)
        groupboxLayout.addWidget(QtGui.QLabel('Frequency [MHz]'),1,0) 
        groupboxLayout.addWidget(self.frequencyCtrl,1,1)
        groupboxLayout.addWidget(QtGui.QLabel('Power [dBm]'),2,0) 
        groupboxLayout.addWidget(self.powerCtrl,2,1)
        groupboxLayout.addWidget(self.stateButton,0,0,1,1)
        groupboxLayout.addWidget(self.updateButton,0,1,1,1)
        groupboxLayout.addWidget(self.maximumButton)

        self.setLayout(superLayout)
    
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        from labrad import types as T
        self.T = T
        self.cxn = yield connectAsync('192.168.169.30')
        self.server = yield self.cxn.marconi_server
        self.tds = yield self.cxn.tektronix_tds_server
        self.SMAGPIB = 'cct_camera GPIB Bus - GPIB0::1'
        try:
            #yield self.server.select_device('GPIB Bus - USB0::0x0AAD::0x0054::102542')
            ##yield self.tds.select_device(self.
            yield self.server.select_device(self.SMAGPIB)
        except Error:
            self.setEnabled(False)
            return
        self.update(0)
        self.powerCtrl.valueChanged.connect(self.onPowerChange)
        self.frequencyCtrl.valueChanged.connect(self.onFreqChange)
        self.stateButton.clicked.connect(self.onOutputChange)
        self.updateButton.clicked.connect(self.update)
        self.maximumButton.clicked.connect(self.checkMax)
    
    @inlineCallbacks
    def onOutputChange(self, state):
        if self.state:
            self.stateButton.setText('Trap Drive   : OFF')
            yield self.server.onoff(False)
        if not self.state:
            self.stateButton.setText('Trap Drive: ON')
            yield self.server.onoff(True)
        self.state = not self.state

        
    @inlineCallbacks
    def update(self, c):
        currentpower = yield self.server.amplitude()
        currentfreq = yield self.server.frequency()
        currentstate = yield self.server.onoff()
        self.powerCtrl.setValue(currentpower)
        self.frequencyCtrl.setValue(currentfreq)
        if currentstate:
            self.stateButton.setText('Trap Drive: ON')
        else:
            self.stateButton.setText('Trap Drive: OFF')
        self.state = currentstate
        
    @inlineCallbacks
    def onFreqChange(self, f):
        yield self.server.frequency(self.T.Value(self.frequencyCtrl.value(), 'MHz'))

    @inlineCallbacks
    def onPowerChange(self, p):
        yield self.server.amplitude(self.T.Value(self.powerCtrl.value(), 'dBm'))

    @inlineCallbacks
    def checkMax(self):
        import labrad
        import numpy
        import time
        import labrad.units as U
        WithUnit = U.WithUnit
        cxn = labrad.connect('192.168.169.29')
        cameracomputercxn = labrad.connect()
        
        #tds = cameracomputercxn.tektronixtds_server()
        tds.select_device()

        #
        #
        #
        # change frequency step size when there is less noise

        f=server.frequency() #in MHz set frequency
        print f
        prev = tds.getvalue()     #previous pk2pk value in volts
        print prev
        f=server.frequency(f+0.01) #change f +.01

        while (True):
            curr = tds.getvalue() #current pk2pk value in Volts
    
            if curr>prev:
                print 'case 1'
                prev=curr                   #set previous pk2pk to current pk2pk
                f=server.frequency(f+0.01) #change f +.01
            elif curr<prev:
                print 'case 2'
                f=server.frequency(f-0.02) #change f -.02
                actual=tds.getvalue()
                if actual<prev:
                    print f
                    print prev; print 'V'
                    break
                #else:
                    #curr=prev
        
            else:
                print 'case 3'
                print f; print 'best frequency MHz'
                print curr
                break
                self.maximumButton.setText('Maximum found')

    
    def closeEvent(self, x):
        self.reactor.stop()

class TD_CONTROL(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(TD_CONTROL, self).__init__(parent)
        self.reactor = reactor
        W = self.buildW(reactor)
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()    
        gridLayout.addWidget(W, 1, 0)
        self.setWindowTitle('Trap Drive Control')
        widget.setLayout(gridLayout) 
        self.setCentralWidget(widget)

    def buildW(self, reactor):
        
        W = QtGui.QWidget()
        subLayout = QtGui.QGridLayout()
        subLayout.addWidget(TD(reactor), 1, 0)
        W.setLayout(subLayout)
        return W
                
    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    TD_CONTROL = TD_CONTROL(reactor)
    TD_CONTROL.show()
    reactor.run()
