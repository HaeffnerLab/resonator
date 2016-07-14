from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred

class cctGUI(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(cctGUI, self).__init__(parent)
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.clients.connection import connection
        cxn = connection()
        yield cxn.connect()
        self.create_layout(cxn)

    def create_layout(self, cxn):
        from PMT_CONTROL import pmtWidget
        from common.clients.LINETRIGGER_CONTROL import linetriggerWidget as lineTrig
        from common.clients.readout_histogram import readout_histogram
        self.tabWidget = QtGui.QTabWidget()
        lightControlTab = self.makeLightWidget(reactor)
        voltageControlTab = self.makeVoltageWidget(reactor)
        #control729Widget = self.makecontrol729Widget(reactor, cxn)
        tableopticsTab = self.makeTableOpticsWidget(reactor)
#        sweepTab = self.makeSweepWidget(reactor)
        #histWidget = self.make_histogram_widget(reactor, cxn)
        #self.tabWidget.addTab(histWidget,'&Histogram')
        self.tabWidget.addTab(voltageControlTab,'&Trap Voltages')
        self.tabWidget.addTab(lightControlTab,'&Laser Room')
        #self.tabWidget.addTab(control729Widget, '&729 Control')
        self.tabWidget.addTab(tableopticsTab, '&Table Optics')
#        self.tabWidget.addTab(sweepTab, '&Sweep (Marconi)')

        from common.clients.script_scanner_gui.script_scanner_gui import script_scanner_gui
        script_scanner = script_scanner_gui(reactor, cxn)
        script_scanner.show()

        self.createGrapherTab()

        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(self.tabWidget, 0, 1, 1, 3)
        rightPanel = QtGui.QGridLayout()
        rightPanel.addWidget(readout_histogram(reactor, cxn), 2, 0)
        rightPanel.addWidget(pmtWidget(reactor), 0, 0)
        rightPanel.addWidget(lineTrig(reactor), 1, 0)
        gridLayout.addLayout(rightPanel, 0, 4)
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(gridLayout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('ResonatorGUI')

    def make_histogram_widget(self, reactor, cxn):
        histograms_tab = QtGui.QTabWidget()
        from common.clients.readout_histogram import readout_histogram
        pmt_readout = readout_histogram(reactor, cxn)
        histograms_tab.addTab(pmt_readout, "PMT")
        #from lattice.clients.camera_histogram import camera_histogram
        #camera_histogram_widget = camera_histogram(reactor, cxn)
        #histograms_tab.addTab(camera_histogram_widget, "Camera")
        return histograms_tab


    def createExperimentParametersTab(self):
        self.tabWidget.addTab(self.experimentParametersWidget, '&Experiment Parameters')

    def makeLightWidget(self, reactor):
        from common.clients.CAVITY_CONTROL import cavityWidget
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(multiplexerWidget(reactor),0,1)
        gridLayout.addWidget(cavityWidget(reactor),0,0)
        widget.setLayout(gridLayout)
        return widget

    def makeTableOpticsWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.clients.DDS_CONTROL import DDS_CONTROL
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(DDS_CONTROL(reactor), 0, 0)
        #gridLayout.setRowStretch(1,1)
        #gridLayout.setColumnStretch(1,1)
        widget.setLayout(gridLayout)
        print "asdsadasd: " + str(widget)
        return widget

    def makeVoltageWidget(self, reactor):
        from common.clients.DAC_CONTROL import DAC_Control
        from PMT_CONTROL import pmtWidget
        #from PMT_CONTROL2 import pmtWidget as pmtWidget2
        from TRAPDRIVE_CONTROL_RS import TD_CONTROL
        from TICKLE_CONTROL import Tickle_Control
#        from SHUTTER_CONTROL import SHUTTER
        from common.clients.multiplexer.MULTIPLEXER_CONTROL import multiplexerWidget
#        from SWEEP_CONTROL import SWEEP_CONTROL
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(DAC_Control(reactor), 0, 0)
        rightPanel = QtGui.QGridLayout()
        rightPanel.addWidget(pmtWidget(reactor), 0, 0)       
#        rightPanel.addWidget(SWEEP_CONTROL(reactor), 1, 0)
        bottomPanel = QtGui.QGridLayout()
        bottomPanel.addWidget(Tickle_Control(reactor), 1, 1)
        bottomPanel.addWidget(TD_CONTROL(reactor), 1, 0)
 #       bottomPanel.addWidget(SHUTTER(reactor), 1, 2)
        #gridLayout.addLayout(rightPanel, 0, 1, 2, 1)          
        gridLayout.addLayout(bottomPanel, 1, 0)
        gridLayout.setRowStretch(0, 1)
        #rightPanel.setRowStretch(2, 1)            
        widget.setLayout(gridLayout)
        return widget

    def makeSweepWidget(self, reactor):
        from SWEEP_CONTROL import SWEEP_WIDGET
        return SWEEP_WIDGET(reactor)

    @inlineCallbacks
    def createGrapherTab(self):
        grapherTab = yield self.makeGrapherWidget(reactor)
        self.tabWidget.addTab(grapherTab, '&Grapher')

    @inlineCallbacks
    def makeGrapherWidget(self, reactor):
        widget = QtGui.QWidget()
        from common.clients.pygrapherlive.connections import CONNECTIONS
        vboxlayout = QtGui.QVBoxLayout()
        Connections = CONNECTIONS(reactor)
        @inlineCallbacks
        def widgetReady():
            window = yield Connections.introWindow
            vboxlayout.addWidget(window)
            widget.setLayout(vboxlayout)
        yield Connections.communicate.connectionReady.connect(widgetReady)
        returnValue(widget)

    def makecontrol729Widget(self, reactor, cxn):
        from common.clients.control_729.control_729 import control_729
        widget = control_729(reactor, cxn)
        return widget

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    cctGUI = cctGUI(reactor)
    cctGUI.show()
    reactor.run()

