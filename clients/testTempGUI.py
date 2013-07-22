import labrad
from time import *
import os
import sys
from PyQt4 import QtGui, QtCore
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
#from test import getValue

from random import *

Thermometers = ["Cold Finger","Inside Heat Shield","Cernox","C1","C2"]

class tempWidget(QtGui.QWidget):
    def __init__(self, thermometerName, parent=None):
        QtGui.QWidget.__init__(self,parent=parent)
        self.thermometerName = thermometerName
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

        self.lcd.display(uniform(0.5,1.6))
        self.lcd.update()
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
        temp = uniform(0.5,1.6)
        self.lcd.display(temp)
        self.lcd.update()

    def selfUpdate(self):
        print ""

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

if __name__ =="__main__":
    main()
