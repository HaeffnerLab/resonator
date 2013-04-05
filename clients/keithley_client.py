import labrad
import numpy
import time
from voltage_conversion import voltage_conversion as VC
import csv

cxn = labrad.connect()
kdmm = cxn.keithley_2100_dmm()
kdmm.select_device()

run_time=time.strftime("%d%m%Y_%H%M")
filedirectly_526='c:/data_resonator_voltage/BNC526_keithley_DMM_'+run_time+'.csv'
filedirectly_529='c:/data_resonator_voltage/BNC529_keithley_DMM_'+run_time+'.csv'

file_526=open(filedirectly_526,"W")
fcsv_526=csv.writer(file_526,lineterminator="\n")
fcsv_526.writerow(["time (Hour:Minute)", "voltage(V)",  "temperature(K)"])
file_526.close()

file_529=open(filedirectly_529,"W")
fcsv_529=csv.writer(file_529,lineterminator="\n")
fcsv_529.writerow(["time(Hour:Minute)", "voltage(V)",  "temperature(K)"])
file_529.close()

vc = VC()

while(1):
    file_526=open(filedirectly_526,"a")
    fcsv_526=csv.writer(file_526,lineterminator="\n")
    voltage = kdmm.get_dc_volts()
    tempK=vc.conversion(voltage)
    fcsv_526.writerow([time.strftime("%H"+":"+"%M"),voltage,tempK])
    file_526.close()
    time.sleep(30)

    filen_529=open(filedirectly529,"a")
    fcsv_529=csv.writer(file_529,lineterminator="\n")
    voltage = kdmm.get_dc_volts()
    tempK=vc.conversion(voltage)
    fcsv_529.writerow([time.strftime("%H"+":"+"%M"),voltage,tempK])
    file_529.close()
    time.sleep(30)


