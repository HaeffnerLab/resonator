from time import sleep
from PyQt4 import QtGui, QtCore
import sys

#name of the python file in which the current as a function of 
        #temperature is defined (  new_current()  )
        # needs to implement a function new_current() which takes as input
        # a float (temperature in Kelvin) and returns a float (current in amps)
import auto_heat_profile

from twisted.internet.defer import inlineCallbacks, returnValue
import pyqtgraph as pg
import numpy as np

# a GUI to control the heater
class HeaterWindow(QtGui.QWidget):

    #height and width in pixels
    sx = 200
    sy = 200
    title = 'Heater Control'
    CURR_MIN = 0
    CURR_MAX = 0.4

    VOLT_MIN = 0
    VOLT_MAX = 60

    #WINDOWS_MACHINE_IP = '192.168.169.30'
    WINDOWS_MACHINE_IP = 'localhost'

    AUTO_TIMESTEP = 2
    NUM_PROF_SAMP = 10000

    def __init__(self, reactor):
        super(HeaterWindow,self).__init__()
        print "heater control starting..."
        
        #necessary in order to join ResonatorGUI event loop
        self.reactor = reactor
	
	#temperature, as float
        self.temp = 9999
	
	#current, as float
	self.curr = 9999

        
        self.prof_module = auto_heat_profile
	self.voltmax = HeaterWindow.VOLT_MAX

        self._connect_external()
        self._makeGUI()
        self._connect_buttons()

        
        from keithley_helper import voltage_conversion as VC
        self.vc = VC()


        self.autoflag = False
        self.profile = None 
        print "heater control on"
        
    def _makeGUI(self):
      
        self.resize(HeaterWindow.sx, HeaterWindow.sy)
        self.setWindowTitle(HeaterWindow.title)
        
        layout = QtGui.QGridLayout()
        autobox = QtGui.QGroupBox('Auto Control')
        manualbox = QtGui.QGroupBox('Manual control')
        
        autolayout = QtGui.QGridLayout()
        manuallayout = QtGui.QGridLayout()
        
        self.setLayout(layout)
        layout.addWidget(autobox, 0, 1)
        layout.addWidget(manualbox, 0, 0)
        
        autobox.setLayout(autolayout)
        manualbox.setLayout(manuallayout)
        
        self.tempread = QtGui.QLabel()
        
        self.pressureRead =QtGui.QLabel()
        
        self.currentbox = QtGui.QDoubleSpinBox()
        self.currentset = QtGui.QPushButton('Set Current')
        self.voltagebox = QtGui.QDoubleSpinBox()
        self.voltageset = QtGui.QPushButton('Set Voltage limit')
       
        self.onBtn = QtGui.QPushButton('Output On')
        self.offBtn = QtGui.QPushButton('Output Off')
        self.srclabel = QtGui.QLabel('defined in {0}'.format(self.rpr))
       
        self.autotoggle = QtGui.QCheckBox('Auto control enabled')
        
        #manuallayout.addWidget(self.updatebtn, 2, 0)
        
        
        layout.addWidget(QtGui.QLabel('Temp, K'), 1, 0)
        layout.addWidget(self.tempread, 1, 1)

        layout.addWidget(QtGui.QLabel('Pressure, mbar'), 2, 0)
        layout.addWidget(self.pressureRead, 2, 1)

        layout.addWidget(QtGui.QLabel('Voltage Limit, V'), 3, 0)
        layout.addWidget(self.voltagebox, 3, 1)
        layout.addWidget(self.voltageset, 3, 2)
        layout.addWidget(self.onBtn, 4, 0)
    #@inlineCallbacks
        layout.addWidget(self.offBtn, 4, 1)
        
        manuallayout.addWidget(QtGui.QLabel('Current, amps'), 1, 0)
        manuallayout.addWidget(self.currentbox, 1, 1)
        manuallayout.addWidget(self.currentset, 1, 2)
        
        autolayout.addWidget(self.autotoggle, 0, 0)
        autolayout.addWidget(self.srclabel, 1, 0)
        
        self.prof_plotter = pg.PlotWidget()
        autolayout.addWidget(self.prof_plotter, 0, 1)
        self.pi = self.prof_plotter.getPlotItem()

        self.pi.setTitle('Heating Profile')
        self.pi.setLabel('bottom', 'Temp.', 'K')
        self.pi.setLabel('left', 'Current', 'A')
        self.prof_plotter.resize(600, 300)

        self.sample_temp = np.linspace(4, 300, HeaterWindow.NUM_PROF_SAMP)
        self.p1btn = QtGui.QRadioButton('std')
        self.p2btn = QtGui.QRadioButton('fast')
        self.p3btn = QtGui.QRadioButton('faster')
        self.p4btn = QtGui.QRadioButton('fastest')
        
        autolayout.addWidget(self.p1btn, 1, 3)
        autolayout.addWidget(self.p2btn, 2, 3)
        autolayout.addWidget(self.p3btn, 3, 3)
        autolayout.addWidget(self.p4btn, 4, 3)

        self.profile_keys = { 'std': 'step_std', 'fast': 'step_fast', 'faster': 'step_faster', 'fastest': 'step_fastest'}

        self.profile_buttons = [self.p1btn, self.p2btn, self.p3btn, self.p4btn]



    def _connect_buttons(self):
	self.currentset.clicked.connect(self.apply_currentbox)
	self.currentbox.setRange(HeaterWindow.CURR_MIN, HeaterWindow.CURR_MAX)
	self.autotoggle.stateChanged.connect(self.togglemode)
	self.voltageset.clicked.connect(self.apply_voltagebox)
	self.voltagebox.setRange(HeaterWindow.VOLT_MIN, HeaterWindow.VOLT_MAX)
	self.onBtn.clicked.connect(self.output_on)
	self.offBtn.clicked.connect(self.output_off)
        self.p1btn.clicked.connect(self.set_profile)
        self.p2btn.clicked.connect(self.set_profile)
        self.p3btn.clicked.connect(self.set_profile)
        self.p4btn.clicked.connect(self.set_profile)




    @inlineCallbacks
    def _connect_external(self):

        #don't import labrad globally, it screws with the reactor choice
        from labrad.wrappers import connectAsync as labrad_connect


        self.rpr = str(self.prof_module).replace('from', 'from\n')


        self.cxn = yield labrad_connect(HeaterWindow.WINDOWS_MACHINE_IP)
        #self.cxn = yield labrad_connect()
        #server for the dmm
        self.dmm = yield self.cxn.keithley_2100_dmm
        try:
            yield self.dmm.select_device()
            
        except:
            print("dmm not present")
            raise Exception

        #server for the heater power supply
        self.ps = yield self.cxn.keithley_2220_30_1()
        try:
            yield self.ps.select_device()
        except:
            print("power supply not present")
            raise Exception

        self.gauge = self.cxn.pfeiffer_pressure_gauge
         

        yield self.autoUpdate()
        self.output_off()
        

    def set_profile(self):
        for btn in self.profile_buttons:
            if btn.isChecked():
                self.profile = self.profile_keys[str(btn.text())]
        self.update_profile_plot()        
                
    def update_profile_plot(self):
        self.pi.clear() 
        self.sample_curr = np.array(map(self.get_auto_current, self.sample_temp))
        self.pi.plot(self.sample_temp, self.sample_curr)



    @inlineCallbacks
    def gettemp(self):
	v = yield self.dmm.get_dc_volts()
        t = self.vc.conversion(v)
        returnValue(t)


    @inlineCallbacks
    def getPressure(self):
        ### returns pressure in mbar as a float
        p = yield self.gauge.readpressure()
        try:
            mbar = p.inUnitsOf('bar').value * 1000.0
            returnValue(mbar)
        except AttributeError:
            returnValue(p)
        

    @inlineCallbacks
    def getcurr(self):

	i = yield self.ps.current()
        returnValue(i)
    



    
    @inlineCallbacks	
    def getvoltmax(self):
        
	v = yield self.ps.voltage()
        returnValue(v)

    @inlineCallbacks
    def update(self, dummy=None):
        #update the temperature and current readings	
        # the generator returns a Deferred. execution here resumes when the
        #deferred fires due to returnValue(), and self.temp gets the result (float!)
        #self.temp = yield self.gettemp()

        #self.tempread.setText(str(self.temp))      

        yield self.updatetemp(dummy)
        yield self.updatepressure(dummy)

        #now do the same for the current and voltage
        self.curr = yield self.getcurr()
        

        self.voltmax = yield self.getvoltmax()
        self.currentbox.setValue(self.curr)
        self.voltagebox.setValue(self.voltmax)
       

    @inlineCallbacks
    def updatetemp(self, dummy=None):
        self.temp = yield self.gettemp()
        self.tempread.setText(str(self.temp))


    @inlineCallbacks
    def updatepressure(self, dummy=None):
        self.pressure = yield self.getPressure()
        self.pressureRead.setText(str(self.pressure))

    def setcurrent(self, curr):
        if curr >= HeaterWindow.CURR_MAX:
	    curr= HeaterWindow.CURR_MAX
        self.ps.current(curr)
        self.update()

    def setvoltage(self, volt):
        if volt >= HeaterWindow.VOLT_MAX:
	    volt = HeaterWindow.VOLT_MAX
	self.ps.voltage(volt)
        self.update()


    def get_auto_current(self, temp):
        if self.profile is None:
            return 0
        else:
            return self.prof_module.new_current(temp, self.profile)


    def apply_currentbox(self, dummy=None):
        # set a new current output/limit for the power supply     
       
        curr = self.currentbox.value()

        self.setcurrent(curr)
    
    def apply_voltagebox(self, dummy=None):
        voltmax = self.voltagebox.value()
        self.setvoltage(voltmax)
        
    def autoON(self):
	self.autoflag = True
	self.currentset.setEnabled(False)

        self.autoUpdate()

    def autoOFF(self):
	self.autoflag = False
	self.currentset.setEnabled(True)
        self.setcurrent(0.00)


    def togglemode(self):
	sw = self.autotoggle.checkState()
	if sw:
	    self.autoON()
	else:
	    self.autoOFF()

    @inlineCallbacks
    def autoUpdate(self):
        """update current based on temp automatically"""
        yield self.updatetemp()
        yield self.updatepressure()

        if self.autoflag:
            nc = self.get_auto_current(self.temp)
            self.setcurrent(nc)

        self.reactor.callLater(HeaterWindow.AUTO_TIMESTEP, self.autoUpdate)
        


    def output_off(self):
        self.currentset.setEnabled(False)
        self.autotoggle.setEnabled(False)
        self.voltageset.setEnabled(False)
        self.onBtn.setEnabled(True)
        self.offBtn.setEnabled(False)
        self.setcurrent(0)
        self.setvoltage(0)
        #self.update()
        
    def output_on(self):
        self.currentset.setEnabled(True)
        self.autotoggle.setEnabled(True)
        self.voltageset.setEnabled(True)      
        self.onBtn.setEnabled(False)
        self.offBtn.setEnabled(True)
        self.setcurrent(0)
        self.setvoltage(HeaterWindow.VOLT_MAX)
        #self.update()
        

#this runs as a script
#
if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    h = HeaterWindow(reactor)
    h.show()
    reactor.run()
