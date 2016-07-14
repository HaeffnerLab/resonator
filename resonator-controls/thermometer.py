import labrad
import labrad.units as U
import numpy as np
from keithley_helper import voltage_conversion as VC


class Thermometer(object):
    """ returns temperature on request using specified DMM server"""
    def __init__(self, dmm_server):
        self.dmm = dmm_server
        #make sure a device is present
        self.dmm.select_device()
        self.vc = VC()
        
    def getTemp(self):
        """returns temp as labrad value in K"""
        #voltage from thermometer
        voltage = self.dmm.get_dc_volts()

        #convert to temp
        return self.vc.conversion(voltage)

