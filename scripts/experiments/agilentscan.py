import labrad
from common.abstractdevices.script_scanner.scan_methods import experiment
from numpy import linspace
import time

class scan_signalgen(experiment):
    
    name = 'Scan Signalgen'
    required_parameters = [
                           ('AgilentScans','average'),
                           ('AgilentScans','cavity_scan'),
                           ('AgilentScans','point_delay'),
                           ('AgilentScans','moving_resolution'),
                           ]
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        cxnlab = labrad.connect('192.168.169.30')
        self.ld = cxnlab.agilent_server
        self.pmt = cxn.normalpmtflow
        self.dv = cxn.data_vault
        self.average = int(self.parameters.AgilentScans.average)
        self.resolution = self.parameters.AgilentScans.moving_resolution
        self.point_delay = self.parameters.AgilentScans.point_delay['s']
        minim,maxim,steps = self.parameters.AgilentScans.cavity_scan
        self.minim = minim = minim['MHz']; self.maxim = maxim = maxim['MHz']
        self.scan = linspace(minim, maxim, steps)  
        self.navigate_data_vault()

    def navigate_data_vault(self):
        self.dv.cd(['','AgilentScans'],True)
        self.dv.new('Agilent Scan {}'.format(self.cavity_name),[('Agilent Frequency', 'MHz')], [('PMT Counts','Counts','Counts')] )
        self.dv.add_parameter('plotLive',True)
    
    def run(self, cxn, context):
        steps = abs(self.init_voltage - self.minim) / float(self.resolution)
        #performing scan
        for i,frequency in enumerate(self.scan):
            self.ld.setvoltage(frequency)
            self.current = frequency
            counts =  self.pmt.get_next_counts('ON',self.average,True)
            self.dv.add([frequency,counts])
            time.sleep(self.point_delay)
            should_stop = self.pause_or_stop()
            if should_stop: return
            self.update_progress(i)

    def update_progress(self, iteration):
        progress = self.min_progress + (self.max_progress - self.min_progress) * float(iteration + 1.0) / len(self.scan)
        self.sc.script_set_progress(self.ident,  progress)        
        
    def finalize(self, cxn, context):
        #back to inital voltage
        steps = abs(self.init_frequency - self.current) / float(self.resolution)
        for voltage in linspace(self.current, self.init_frequency, steps):
            self.ld.setfrequency(frequency)
            time.sleep(self.point_delay)  
            
if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = scan_signalgen(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
