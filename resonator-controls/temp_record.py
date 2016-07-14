"""record temperature time-series from the thermometer which is connected to the Keithley 2100"""

import labrad
import numpy as np
import time
from time import sleep, localtime
import sys

WINDOWS_MACHINE_IP= '192.168.169.30'

REC_TIME = 24*3600  #time to record, in seconds
DT = 10         # time between samples, in seconds


cxn = labrad.connect(WINDOWS_MACHINE_IP)

tm = localtime()

yr = tm.tm_year
mon = tm.tm_mon
dy = tm.tm_mday
hr = tm.tm_hour
mn = tm.tm_min
sec = tm.tm_sec

tag = ''
strings = sys.argv
try:
    i = strings.index('-n')
    tag = strings[i+1]
except ValueError:
    print "no name tag (-n) provided"


i = None
try: 
    i = strings.index('-t')
except ValueError:
    print "no time provided, using default"

fname = time.strftime("%Y-%m-%d,%H:%M:%S")+ "-temp-{0}.csv".format(tag)



if not (i is None):
    REC_TIME = int(strings[i+1]) * 3600


dmm = cxn.keithley_2100_dmm()
dmm.select_device()
from keithley_helper import voltage_conversion as VC

converter = VC()

nsamp = int(REC_TIME / DT)

data = np.zeros((nsamp, 2))
       
header_str = "recording time = {0} hrs, start time = {1}".format( REC_TIME/3600, time.strftime("%Y-%m-%d,%H:%M:%S"))
print header_str
print "saving to ", fname

for i in range(nsamp):
    try:
        v = dmm.get_dc_volts()
        temp = converter.conversion(v)
        data[i,0] = i*DT
        data[i,1] = temp
        print temp
        sleep(DT)
    except:
        break

np.savetxt(fname, data, header=header_str)
