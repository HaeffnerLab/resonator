import labrad
import os
from PyQt4 import QtGui, QtCore
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

Thermometers = ["Cold Finger","Inside Heat Shield","Cernox","C1","C2"]

class tempPanel(QtGui.QWidget):
    def __init__(self, parent, thermometerName):
        super(tempPanel,self).__init__(parent)
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.reactor = reactor
        self.thermometerName = thermometerName
        self.setupUI()
        self.connect()
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        cxn_pulser = yield connectAsync()
        cxn_dmm = yield connectAsync('192.168.169.30')
        self.server_pulser = cxn_pulser.pulser
        self.server_dmm = cxn_dmm.keithley_2110_dmm
        
    def setupUI(self):
        tempLabel = QtGui.QLabel()
        tempLabel.setText(tempLabel.tr("Temperature (K)"))
        thermometerName = QtGui.QLabel(self.thermometerName)
        thermometerName.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        
        self.temperatureBox = QtGui.QLCDNumber()
        self.temperatureBox.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=24))
        self.temperatureBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)
        
        self.grid.addWidget(tempLabel, 2, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(thermometerName, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.temperatureBox, 2, 1, QtCore.Qt.AlignCenter)
        
        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

    @inlineCallbacks
    def pulser(self):
        yield self.server_pulser.switch_manual()
    
    def getVoltage(self):
        yield server_dmm.get_dc_volts()
        
    @inlineCallbacks
    def newValue(self, newTemp):
        yield QtGui.QLCDNumber().display(newTemp)
    
    

class Layout(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Layout, self).__init__(parent)
        self.setupUI()
        self.connect()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        cxn_pulser = yield connectAsync()
        cxn_dmm = yield connectAsync('192.168.169.30')
        self.server_pulser = cxn_pulser.pulser
        self.server_dmm = cxn_dmm.keithley_2110_dmm
    
    def setupUI(self):
        self.setWindowTitle('Resonator Temperature')
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)
#        devPanel = tempPanel(reactor)
#         thermometerName = ["Cold Finger","Inside Heat Shield","Cernox","C1","C2"]
#         numThermometer = len(thermometerName)
#         for i in range(numThermometer):
#             devPanel = tempPanel(thermometerName[0])
#             self.devDict[i] = devPanel
#             if (i % 2 == 0): #even
#                 grid.addWidget(devPanel, (i / 2) , 0)
#             else:
#                 grid.addWidget(devPanel, ((i - 1) / 2) , 1)
        grid.addWidget(tempPanel(self, "Cold Finger"), 1 , 1)
        grid.addWidget(tempPanel(self, "Inside Heat Shield"), 1 , 2)
        grid.addWidget(tempPanel(self, "Cernox"), 2, 1)
        grid.addWidget(tempPanel(self, "C1"), 2 , 2)
        grid.addWidget(tempPanel(self, "C2"), 2 , 3)
        
        self.show()
        
def main():
    a = QtGui.QApplication( [] )
    tempGUI = Layout()
    tempGUI.show()
    a.exec_()

if __name__ == '__main__':
     main()
