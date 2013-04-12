import labrad
import numpy
import time
from voltage_conversion import voltage_conversion as VC
import csv

cxn = labrad.connect()
kdmm = cxn.keithley_2100_dmm()
kdmm.select_device()

run_time=time.strftime("%d%m%Y_%H%M")
#BNC 526 is at Cold Finger
filedirectly_526='c:/data_resonator_voltage/keithley_DMM_'+run_time+'/526(Cold Finger).csv'
#BNC 529 is inside the heat shield
filedirectly_529='c:/data_resonator_voltage/keithley_DMM_'+run_time+'/529(Inside Heat Shield).csv'

file_526=open(filedirectly_526,"wb")
fcsv_526=csv.writer(file_526,lineterminator="\n")
fcsv_526.writerow(["time passed (minutes)", "current time", "voltage(V)", "temperature(K)"])
file_526.close()

file_529=open(filedirectly_529,"wb")
fcsv_529=csv.writer(file_529,lineterminator="\n")
fcsv_529.writerow(["time passed (minutes)", "current time", "voltage(V)", "temperature(K)"])
file_529.close()

vc = VC()
minutes_526=0
minutes_529=0.5
while(1):
    file_526=open(filedirectly_526,"ab")
    fcsv_526=csv.writer(file_526,lineterminator="\n")
    voltage = kdmm.get_dc_volts()
    tempK=vc.conversion(voltage)
    fcsv_526.writerow([minutes_526,time.strftime("%H"+":"+"%M"),voltage,tempK])
    file_526.close()
    time.sleep(30)
    minutes_526+=1

    file_529=open(filedirectly_529,"ab")
    fcsv_529=csv.writer(file_529,lineterminator="\n")
    voltage = kdmm.get_dc_volts()
    tempK=vc.conversion(voltage)
    fcsv_529.writerow([minutes_529,time.strftime("%H"+":"+"%M"),voltage,tempK])
    file_529.close()
    time.sleep(30)
    minutes_529+=1


