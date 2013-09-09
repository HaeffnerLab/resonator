import labrad
from time import *
import numpy as np
from PyQt4 import QtGui, QtCore
from twisted.internet.task import LoopingCall
from twisted.internet.defer import inlineCallbacks, returnValue
from keithley_helper import voltage_conversion as VC
from keithley_helper import resistance_conversion as RC

vc=VC()
rc=RC()

run_time = strftime("%d%m%Y_%H%M")
initial_time = time()
Thermometers = ["Cold finger", "Inside Heat Shield", "C1", "C2", "Cernox"]

class tempWidget(QtGui.QWidget):
    def __init__(self, reactor, thermometerName):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.updater = LoopingCall(self.update)
        self.thermometer_dict = {}.fromkeys(Thermometers)
        self.fileDirectory = "/home/resonator/Desktop/test/"+str(self.thermometerName)+"_"+run_time+"_keithley_DMM.csv"
        self.thermometerName = thermometerName
        self.initializeFiles()
        self.connect()
        self.setupUI()
    

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn_pulser = yield connectAsync()
        self.cxn_dmm = yield connectAsync('192.168.169.30')
        self.pulserServer = yield self.cxn_pulser.pulser
        self.dmmServer = yield self.cxn_dmm.keithley_2110_dmm
        self.dmmServer.select_device()


    def initializeFiles(self):
        numThermometers = len(Thermometers)
        for i in range(numThermometers):
            fileDirectory = "/home/resonator/Desktop/test/"+str(self.thermometerName)+"_"+run_time+"_keithley_DMM.csv"
            openFile = open(fileDirectory, "wb")
            openFile.close()
            
            
    def setupUI(self):
        tempLabel = QtGui.QLabel()
        tempLabel.setText(tempLabel.tr("Temperature (K)"))
        thermometerName = QtGui.QLabel(self.thermometerName)
        thermometerName.setFont(QtGui.QFont("MS Shell Dlg 2", pointSize = 16))

        self.tempBox = QtGui.QLCDNumber(parent = self)
        self.tempBox.setFont(QtGui.QFont("MS Shell Dlg 2", pointSize = 24))
        self.tempBox.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.tempBox.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.tempBox.setDigitCount(7)

        self.grid = QtGui.QGridLayout()
        self.grid.setSpacing(5)
        self.grid.addWidget(thermometerName, 1, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(tempLabel, 2, 0, QtCore.Qt.AlignCenter)
        self.grid.addWidget(self.tempBox, 2, 1, QtCore.Qt.AlignCenter)

        self.setLayout(self.grid)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.show()

    @inlineCallbacks
    def update(self):
        yield self.pulserServer.switch_manual(self.thermometerName, "True")
        voltage = yield self.dmmServer.get_dc_volts()
        temp = yield self.processData(voltage)
        self.tempBox.display(temp)
        yield self.tempBox.update()
#         yield None
#         for key,widget in ...:
#                 voltage = yield self.get_voltage_from_server()
#                 gui.set_voltage(voltage)
        yield self.pulserServer.switch_manual(self.thermometerName, "False")

    
    def processData(self, v):
        self.dataSet = [0, 0]
        self.dataSet[0] = v
        ###################################################################################
        #Load calibraton files and get ready for temperature lookup
        V529 = np.loadtxt('calibration files/529(Inside Heat Shield)_28062013_1107_keithley_DMM.csv',delimiter=',')
        V529 = V529.transpose()
        C1 = np.loadtxt('calibration files/C1_28062013_1107_keithley_DMM.csv',delimiter=',')
        C1 = C1.transpose()
        C2 = np.loadtxt('calibration files/C2_28062013_1107_keithley_DMM.csv',delimiter=',')
        C2 = C2.transpose() 
        Cernox = np.loadtxt('calibration files/Cernox_28062013_1107_keithley_DMM.csv',delimiter=',')
        Cernox = Cernox.transpose()
        TempC1 = np.interp(C1[0], V529[0], V529[3])
        TempC2 = np.interp(C2[0], V529[0], V529[3])
        TempCernox = np.interp(Cernox[0], V529[0], V529[3])

        TempC1 = TempC1[::-1]
        TempC2 = TempC2[::-1]
        TempCernox = TempCernox[::-1]
        VoltC1 = C1[2][::-1]
        VoltC2 = C2[2][::-1]
        VoltCernox = Cernox[2][::-1]
        TempV529=V529[3][::-1]
        VoltV529=V529[2][::-1]    
        ###################################################################################
        if self.thermometerName == "C1":
            self.dataSet[1]=np.interp(self.dataSet[0],VoltC1,TempC1)
                
        elif self.thermometerName == "C2":
            self.dataSet[1]=np.interp(self.dataSet[0],VoltC2,TempC2)
        
        elif self.thermometerName == "Cernox":
            self.dataSet[1]=np.interp(self.dataSet[0],VoltCernox,TempCernox)
        
        else:
            self.dataSet[1] = vc.conversion(self.dataSet[0])
        
        openFile = open(self.fileDirectory, "ab")
        csvFile = writer(openFile, lineterminator="\n")
        elapsed_time = (time() - (initial_time))/60
        csvFile.writerow([round(elapsed_time,4), strftime("%H"+"%M"), self.dataSet[0], round(self.dataSet[1], 3)])
        openFile.close()
        
        return self.dataSet[1]

    def start(self, state):
        if state == QtCore.Qt.Checked:
            self.updater.start(1)
        elif state == QtCore.Qt.Unchecked:
            self.updater.stop()
            
        
class tempMeasurement(QtGui.QWidget):
    def __init__(self, reactor):
        QtGui.QWidget.__init__(self)
        self.reactor = reactor
        self.tempLayout()
    
    def tempLayout(self):
        Thermometers = ["Cold Finger","Inside Heat Shield","C1","C2", "Cernox"]
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.setLayout(grid)
        
        self.checkBox = QtGui.QCheckBox('Take Data', self)
        
        numThermometers = len(Thermometers)
        for i in range(numThermometers):
            tempUI = tempWidget(reactor, Thermometers[i])
#            dict[Thermometers[i]] = tempUI
           # self.checkBox.stateChanged.connect(tempUI.start)
            self.checkBox.stateChanged.connect(tempUI.start)
            if (i % 2 == 0): #even
                grid.addWidget(tempUI, (i / 2) , 1)
            else:
                grid.addWidget(tempUI, ((i - 1) / 2) , 2)
        self.setLayout(grid)
        self.setWindowTitle("Resonator Temperature")
        self.show()

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    mainPanel = tempMeasurement(reactor)
    reactor.run()
