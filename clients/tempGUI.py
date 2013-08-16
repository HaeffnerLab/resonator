import labrad
import sys
import threading
import numpy as np
from time import *
from PyQt4 import QtGui, QtCore
from keithley_helper import voltage_conversion as VC
from keithley_helper import resistance_conversion as RC
from twisted.internet.defer import inlineCallbacks, returnValue

vc=VC()
rc=RC()

run_time = strftime("%d%m%Y_%H%M")
initial_time = time()
Thermometers = ["Cold Finger","Inside Heat Shield","C1","C2", "Cernox"]

class Measurement(QtGui.QWidget):
    cxn_dmm = labrad.connect("192.168.169.30")
    cxn_pulser = labrad.connect()
    dmmServer = cxn_dmm.keithley_2110_dmm
    dmmServer.select_device()
    pulserServer =  cxn_pulser.pulser
    
    def __init__(self, thermometerName):
        self.stopMeasurement = False
        self.thermometerName = thermometerName
        self.fileDirectory = "/home/resonator/Desktop/test/"+str(self.thermometerName)+"_"+run_time+"_keithley_DMM.csv"
        self.initializeFiles()
        self.setupUI()
        
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

            
    def getValues(self, forever =True):
        while True:
            if stopMeasurement: break
            print "still running..."

            if forever == False: break

    def getMeasurement(self, forever = True):
        ##################################################################################################
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
        ##################################################################################################
        while True:
            if self.stopGUI: break
            thermometer = ""
            self.dataSet = [0, 0]
            Thermometers = ["Cold Finger","Inside Heat Shield","C1","C2", "Cernox"]
            numThermometers = len(Thermometers)
            for i in range(numThermometers):
                thermometer = "Thermometer"+str(i+1)
                self.pulserServer.switch_manual(thermometer, False)
                if Thermometers[i] == self.thermometerName:
                    self.pulserServer.switch_manual(thermometer, True)
                    sleep(0.5)
            
            self.dataSet[0] = self.dmmServer.get_dc_volts()
            voltage = self.dataSet[0]
            if self.thermometerName == "Cold Finger":
                self.dataSet[1] = vc.conversion(self.dataSet[0])
                self.tempBox.display(self.dataSet[1])
                self.tempBox.update()
                self.voltageBox.display(self.dataSet[0])
                self.voltageBox.update()
                sleep(55)

            if self.thermometerName == "Inside Heat Shield":
                self.dataSet[1] = vc.conversion(self.dataSet[0])
                self.tempBox.display(self.dataSet[1])
                self.tempBox.update()
                self.voltageBox.display(self.dataSet[0])
                self.voltageBox.update()
                sleep(56)
                
            elif self.thermometerName == "C1":
                self.dataSet[1]=np.interp(self.dataSet[0],VoltC1,TempC1)
                
            elif self.thermometerName == "C2":
                self.dataSet[1]=np.interp(self.dataSet[0],VoltC2,TempC2)

                
            elif self.thermometerName == "Cernox":
                self.dataSet[1]=np.interp(self.dataSet[0],VoltCernox,TempCernox)
            else:
                self.dataSet[1] = vc.conversion(self.dataSet[0])

            for i in range(numThermometers):
                thermometer = "Thermometer"+str(i+1)
                self.pulserServer.switch_manual(thermometer, False)
            self.tempBox.display(self.dataSet[1])
            self.tempBox.update()
            self.voltageBox.display(self.dataSet[0])
            self.voltageBox.update()

            openFile = open(self.fileDirectory, "ab")
            csvFile = writer(openFile, lineterminator="\n")
            elapsed_time = (time() - (initial_time))/60
            dataSet = self.newValue()
            csvFile.writerow([round(elapsed_time,4), strftime("%H"+"%M"), dataSet[0], round(dataSet[1], 3)])
    #        print str(self.thermometerName)+": Temp = "+ str(dataSet[1]) + "(K) , Voltage = " + str(dataSet[0]) + "(V)"
            openFile.close()
            sleep(60)
            if forever == False: break
            
    def start(self):
        self.t = threading.Thread(target=self.getMeasurement)
        self.t.start()

    def stop(self):
        """shut down continuous measurement."""
        self.stopMeasurement = True

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
            if (i % 2 == 0): #even
                grid.addWidget(tempUI, (i / 2) , 0)
            else:
                grid.addWidget(tempUI, ((i - 1) / 2) , 1)
            tempUI.start()
            sleep(1)
        self.setLayout(grid)
        self.show()
        
def main():
    from twisted.internet import reactor
    a = QtGui.QApplication( [] )
    tempUI= Layout(reactor)
    tempUI.show()
    a.exec_()
    sys.exit(a.exec_())


if __name__ == "__main__":
    main()
