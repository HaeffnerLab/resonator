import labrad
from csv import *
from time import *
from random import *

import os
import sys
from PyQt4 import QtGui, QtCore
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from keithley_helper import voltage_conversion as VC
from keithley_helper import resistance_conversion as RC

vc=VC()
rc=RC()
run_time = strftime("%d%m%Y_%H%M")
initial_time = time()
Thermometers = ["Cold Finger","Inside Heat Shield","Cernox","C1","C2"]

class tempWidget(QtGui.QWidget):
    def __init__(self, thermometerName, parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.thermometerName = thermometerName
        self.fileDirectory = "/Users/ryohmasuda/Desktop/testFile/"+str(self.thermometerName)+"_"+run_time+"_keithley_DMM.csv"
        self.setupUI()

    def setupUI(self):
        tempLabel = QtGui.QLabel()
        tempLabel.setText(tempLabel.tr("Temperature (K)"))
        thermometerName = QtGui.QLabel(self.thermometerName)
        thermometerName.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        
        self.lcd = QtGui.QLCDNumber(parent=self)
        self.lcd.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=24))
        self.lcd.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.lcd.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.lcd.setDigitCount(7)
        self.connect(self.lcd, QtCore.SIGNAL('valueChanged(float)'), self.lcd, QtCore.SLOT('display(float)'))

        self.button = QtGui.QPushButton("Get New Data", parent=self)
        self.button.clicked.connect(self.update)

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)

        self.grid.addWidget(tempLabel, 2, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(thermometerName, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.lcd, 2, 1, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.button, 3,1, QtCore.Qt.AlignCenter)
        
        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        
    def update(self):
<<<<<<< HEAD
        temp = uniform(0,293)
        self.lcd.display(temp)
=======
        self.dataSet = getValue().getTemperature()
        self.measurement(self.dataSet)
        self.lcd.display(self.dataSet[1])
>>>>>>> d1a6830a79da9bfc6c53b7e1ae4b9d7cc0a38959
        self.lcd.update()

    def measurement(self, dataSet):
##        yield self.pulserServer.switch_manual(self.thermometerName, True)
        openFile = open(self.fileDirectory, "ab")
        csvFile = writer(openFile, lineterminator="\n")
#        dataSet = getValue().getTemperature()
        elapsed_time = (time() - (initial_time))/60
        csvFile.writerow([round(elapsed_time,4), strftime("%H"+"%M"), dataSet[0], dataSet[1]])
        print str(self.thermometerName)+": Temp = "+ str(dataSet[1]) + "(K) , Voltage = " + str(dataSet[0]) + "(V)"
        openFile.close()       

class getValue(object):
    def getTemperature(self):
        dataSet = [0, 0]
        dataSet[0] = uniform(0.5005, 1.627)
        dataSet[1] = vc.conversion(dataSet[0])
        return dataSet

def main():
    a = QtGui.QApplication( [] )
    panel = QtGui.QWidget()
    grid = QtGui.QGridLayout()
    grid.setSpacing(10)
    for i in range (len(Thermometers)):
        if (i % 2 == 0):
            grid.addWidget(tempWidget(Thermometers[i], parent=panel), (i/2), 0)
        else:
            grid.addWidget(tempWidget(Thermometers[i], parent=panel), ((i-1)/2), 1)

    panel.setLayout(grid)

    main_window = QtGui.QMainWindow()
    main_window.setWindowTitle("Resonator Temperature")
    main_window.setCentralWidget(panel)

    main_window.show()
    
    a.exec_()

if __name__ == "__main__":
    main()
