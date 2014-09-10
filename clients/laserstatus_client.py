from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks 
from connection import connection

SIGNALlaserstatus=1834332

class laserstatusWidget(QtGui.QFrame):
    def __init__(self,reactor, cxn=None, parent=None)
        super(laserstatusWidget, self).__init__(parent)
        self.initialized = False
        self.reactor = reactor
        self.connect()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('192.168.169.49')
        try:
            self.server = yield self.cxn.laserlockserver
            self.context = yield self.cxn.context()
        except:
            print 'Laserstatus_client:could not connect'
        try:
            yield self.initializeGUI()
            yield self.setupListeners()
        except Exception, e:
            print 'SWTICH CONTROL: Pulser not available'
            self.setDisabled(True)

    @inlineCallbacks
    def setupListeners(self):
        yield self.server.signal__laserlock(SIGNALlaserstatus)
        yield self.server.addListener(listener = self.laserupdate, source = None, ID = SIGNALlaserstatus)


    def laserupdate(self, c, laserstat):
        
