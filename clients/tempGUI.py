import labrad
import os
import sys
import numpy as np
import threading
from csv import *
from PyQt4 import QtGui, QtCore
from random import *
from time import *
from keithley_helper import voltage_conversion as VC
from keithley_helper import resistance_conversion as RC
from twisted.internet.defer import inlineCallbacks, returnValue

vc=VC()
rc=RC()

class tempWidget(QtGui.QWidget):
    def __init__(self, parent, thermometerName):
        QtGui.QWidget.__init__(self, parent=parent)
        self.thermometerName = thermometerName
        self.create_Widget()

    def create_Widget(self):
        tempLabel = QtGui.QLabel()
        tempLabel.setText(tempLabel.tr("Temperature (K)"))
        thermometerName = QtGui.QLabel(self.thermometerName)
        thermometerName.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        
        self.tempBox = QtGui.QLCDNumber(parent=self)
        self.tempBox.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=24))
        self.tempBox.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.tempBox.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.tempBox.setDigitCount(7)

        voltageLabel = QtGui.QLabel()
        voltageLabel.setText(voltageLabel.tr("Voltage (V)"))
        self.voltageBox = QtGui.QLCDNumber(parent=self)
        self.voltageBox.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=24))
        self.voltageBox.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.voltageBox.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.voltageBox.setDigitCount(7)


        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)
        self.grid.addWidget(tempLabel, 2, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(thermometerName, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.tempBox, 2, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(voltageLabel, 3, 0,  QtCore.Qt.AlignCenter)        
        self.grid.addWidget(self.voltageBox, 3, 1,  QtCore.Qt.AlignCenter)

        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        

    def newValue(self, forever = True):
        Thermometers = ["Cold Finger","Inside Heat Shield","C1","C2", "Cernox"]
        while True:
            sleep(5)
            self.dataSet = [0, 0]
            self.dataSet[0] = uniform(0.5, 1.6)
##        #load calibraton files and get ready for temperaturelookup
##        V529 = np.loadtxt('calibration files/529(Inside Heat Shield)_28062013_1107_keithley_DMM.csv',delimiter=',')
##        V529 = V529.transpose()
##        C1 = np.loadtxt('calibration files/C1_28062013_1107_keithley_DMM.csv',delimiter=',')
##        C1 = C1.transpose()
##        C2 = np.loadtxt('calibration files/C2_28062013_1107_keithley_DMM.csv',delimiter=',')
##        C2 = C2.transpose()
##        Cernox = np.loadtxt('calibration files/Cernox_28062013_1107_keithley_DMM.csv',delimiter=',')
##        Cernox = Cernox.transpose()
##        TempC1 = np.interp(C1[0], V529[0], V529[3])
##        TempC2 = np.interp(C2[0], V529[0], V529[3])
##        TempCernox = np.interp(Cernox[0], V529[0], V529[3])
##
##        TempC1 = TempC1[::-1]
##        TempC2 = TempC2[::-1]
##        TempCernox = TempCernox[::-1]
##        VoltC1 = C1[2][::-1]
##        VoltC2 = C2[2][::-1]
##        VoltCernox = Cernox[2][::-1]
##        TempV529=V529[3][::-1]
##        VoltV529=V529[2][::-1]
##        
            thermometer = ""
            numThermometers = len(Thermometers)
##        for i in range(numThermometers):
##            thermometer = "Thermometer"+str(i+1)
##            if (self.thermometerName == Thermometers[i]):
##                self.pulserServer.switch_manual(thermometer, True)
##            else:
##                self.pulserServer.switch_manual(thermometer, False)
##        self.dataSet = [0, 0]
##        self.dataSet[0] = self.dmmServer.get_dc_volts()
##        voltage = self.dataSet[0]
            if self.thermometerName == "C1":
                self.dataSet[1] = 100
##            self.dataSet[1]=np.interp(self.dataSet[0],VoltC1,TempC1)
            elif self.thermometerName == "C2":
                self.dataSet[1] = 200
##            self.dataSet[1]=np.interp(self.dataSet[0],VoltC2,TempC2)
            elif self.thermometerName == "Cernox":
                self.dataSet[1] = 300
##            self.dataSet[1]=np.interp(self.dataSet[0],VoltCernox,TempCernox)        
            else:
                self.dataSet[1] =  vc.conversion(self.dataSet[0])
                
 #           self.dataSet[0] = uniform(0.5, 1.6)
#            self.dataSet[1] = vc.conversion(self.dataSet[0])
            self.tempBox.display(self.dataSet[1])
            self.tempBox.update()
            self.voltageBox.display(self.dataSet[0])
            self.voltageBox.update()
##        for i in range (numThermometers):
##            thermometer = "Thermometer"+str(i+1)
##            self.pulserServer.switch_manual(thermometer, False)
            if forever==False: break
    #        return self.dataSet

    def one_newValue(self):
        print ""

    def updateValue(self):
        """CALL THIS to start running forever."""
        self.t = threading.Thread(target=self.newValue)
        self.t.start()
        
class Layout(QtGui.QWidget):
    def __init__(self, reactor):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.tempLayout()
    
    def tempLayout(self):
        Thermometers = ["Cold Finger","Inside Heat Shield","C1","C2", "Cernox"]
        self.setWindowTitle("Resonator Temperature")
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)
        numThermometers = len(Thermometers)
        for i in range(numThermometers):
            tempUI = tempWidget(self, Thermometers[i])
            tempUI.updateValue()
            if (i % 2 == 0): #even
                grid.addWidget(tempUI, (i / 2) , 0)
            else:
                grid.addWidget(tempUI, ((i - 1) / 2) , 1)
        self.setLayout(grid)
        self.show()

        
def main():
    from twisted.internet import reactor
    a = QtGui.QApplication( [] )
    tempUI= Layout(reactor)
    tempUI.show()
    a.exec_()


if __name__ == "__main__":
    main()
