import labrad
import numpy
import time
import voltage_conversion
import csv
VC=voltage_conversion()

cxn = labrad.connect()
kdmm = cxn.Keithley_2100_DMM()
kdmm.select_device()

filedirectly='c:/data_resonator_voltage/keithley_DMM_'+time.strftime("%d%m%Y_%H%M")+'.csv'
filename=open(filedirectly,"wb")
fcsv=csv.writer(filename,lineterminator="\n")
t=time.strftime("%H%M")
while(1):
    v=kdmm.getdcVolts()
    tempK=VC.converter(v)
    fcsv.writerow([t,v,temp])
    

    #time.sleep(60)
    
