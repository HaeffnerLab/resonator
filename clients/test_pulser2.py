import labrad
import numpy
import time
from voltage_conversion import voltage_conversion as VC
import csv

#cxn = labrad.connect()
#pulse = cxn.pulser()

cxn = yield connectAsync('192.168.169.29')
pulse_server = cxn.pulser()

#keithley = cxn1.keithley_2100_dmm()
#keithley.select_device()


count=0
while(count <= 10):
    pulse_server.switch_manual("11", True)
    count += 1
    sleep(5)
    pulse_server.switch_manual("11", False)
    sleep(5)
