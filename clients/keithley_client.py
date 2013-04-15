import labrad
import numpy
import time
from voltage_conversion import voltage_conversion as VC
import csv

cxn = labrad.connect()
keithley = cxn.keithley_2100_dmm()
keithley.select_device()

run_time = time.strftime("%d%m%Y_%H%M")
initial_time = time.time()
#BNC 526 is at Cold Finger
filedirectory_526 ='c:/data_resonator_voltage/keithley_DMM_'+run_time+'/526(Cold Finger).csv'
#BNC 529 is inside the heat shield
filedirectory_529 ='c:/data_resonator_voltage/keithley_DMM_'+run_time+'/529(Inside Heat Shield).csv'

file_526 = open(filedirectory_526,"wb")
fcsv_526 = csv.writer(file_526,lineterminator="\n")
fcsv_526.writerow(["Elapsed Time (minutes)", "Current Time(H:M)", "Voltage(V)", "Temperature(K)"])
file_526.close()

file_529 = open(filedirectory_529,"wb")
fcsv_529 = csv.writer(file_529,lineterminator="\n")
fcsv_529.writerow(["Elapsed Time (minutes)", "Current Time(H:M)", "Voltage(V)", "Temperature(K)"])
file_529.close()

vc = VC()
while(1):
    file_526=open(filedirectory_526,"ab")
    fcsv_526=csv.writer(file_526,lineterminator="\n")
    voltage = keithley.get_dc_volts()
    tempK=vc.conversion(voltage)
    elapsed_time_526 = (time.time() - initial_time)/60
    fcsv_526.writerow([elapsed_time_526,time.strftime("%H"+":"+"%M"),voltage,tempK])
    file_526.close()
    time.sleep(30)

    file_529 = open(filedirectory_529,"ab")
    fcsv_529 = csv.writer(file_529,lineterminator="\n")
    voltage = keithley.get_dc_volts()
    tempK = vc.conversion(voltage)
    elapsed_time_529 = (time.time() - initial_time)/60
    fcsv_529.writerow([elapsed_time_529,time.strftime("%H"+":"+"%M"),voltage,tempK])
    file_529.close()
    time.sleep(30)
