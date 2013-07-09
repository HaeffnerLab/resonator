from PyQt4 import QtGui, QtCore

Thermometers = ["Cold Finger","Inside Heat Shield","Cernox","C1","C2"]

class DevicePanel(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUI()
        
    def setupUI(self):
        tempLabel = QtGui.QLabel()
        tempLabel.setText(tempLabel.tr("Temperature (K)"))
        thermometer = QtGui.QLabel("Temperature")
        thermometer.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        
        self.temperatureBox = QtGui.QLCDNumber()
        self.temperatureBox.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=20))
#        self.temperatureBox.setDecimals(3)
        self.temperatureBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)
        
        self.grid.addWidget(tempLabel, 2, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(thermometer, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.temperatureBox, 2, 1, QtCore.Qt.AlignCenter)
        
        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
#        self.setWindowTitle('Resonator Temperature')
        self.show()

class Layout(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Layout, self).__init__(parent)
        self.setupUI()
    
    def setupUI(self):
        self.setWindowTitle('Resonator Temperature')
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)
        devPanel = DevicePanel()
#         thermometerName = ["Cold Finger","Inside Heat Shield","Cernox","C1","C2"]
#         numThermometer = len(thermometerName)
#         for i in range(numThermometer):
#             devPanel = DevicePanel(thermometerName[0])
#             self.devDict[i] = devPanel
#             if (i % 2 == 0): #even
#                 grid.addWidget(devPanel, (i / 2) , 0)
#             else:
#                 grid.addWidget(devPanel, ((i - 1) / 2) , 1)
        grid.addWidget(DevicePanel(), 1 , 1)
        grid.addWidget(DevicePanel(), 1 , 2)
        grid.addWidget(DevicePanel(), 1 , 3)
        grid.addWidget(DevicePanel(), 2 , 1)
        grid.addWidget(DevicePanel(), 2 , 2)
        self.show()
        
def main():
    Thermometers = ["Cold Finger","Inside Heat Shield","Cernox","C1","C2"]
    a = QtGui.QApplication( [] )
    tempGUI = Layout()
    tempGUI.show()
    a.exec_()

if __name__ == '__main__':
     main()
