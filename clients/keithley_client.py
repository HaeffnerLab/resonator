import labrad
import numpy
import time
from voltage_conversion import voltage_conversion as VC
import csv
#VC=voltage_conversion

cxn = labrad.connect()
kdmm = cxn.keithley_2100_dmm()
kdmm.select_device()

filedirectly='c:/data_resonator_voltage/keithley_DMM_'+time.strftime("%d%m%Y_%H%M")+'.csv'
filename=open(filedirectly,"wb")
fcsv=csv.writer(filename,lineterminator="\n")

vc = VC()

while(1):
    t=time.strftime("%H%M")
    voltage = kdmm.get_dc_volts()
    tempK=vc.conversion(voltage)
    fcsv.writerow([t,voltage,tempK])
    time.sleep(60)
    
