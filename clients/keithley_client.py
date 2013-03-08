import labrad
import numpy
import time
import voltage_conversion
import csv
VC=voltage_conversion()

cxn = labrad.connect()
kdmm = cxn.Keithley_2100_DMM()

filename='c:/data_resonator/Voltage_Temperature/keithley_DMM_'+time.strftime("%d%m%Y_%H%M")+'.csv'
#numpy.savetxt(filename,time.strftime("%H%M"),voltage,tempK)
fcsv=csv.writer(file(filename,"w"),lineterminator="\n")
t=time.strftime("%H%M")
while(1):
    optstr=""
    v=kdmm.getdcVolts()
    tempK=VC.converter(v)
    fcsv.writerow([t,v,temp])
    

    #time.sleep(60)
    