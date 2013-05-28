import labrad
import time
from voltage_conversion import voltage_conversion as VC
import csv

#Run on the Linux
cxn = labrad.connect()
pulser = cxn.pulser()
#Connect to Windows Computer to use Keithley DMM
cxndmm = labrad.connect('192.168.169.30')
keithley = cxndmm.keithley_2100_dmm()
keithley.select_device()


#Initially switch off the TTL pulse except the first one
pulser.switch_manual('Thermometer1', False)
pulser.switch_manual('Thermometer2', True)
pulser.switch_manual('Thermometer3', True)
pulser.switch_manual('Thermometer4', True)

run_time = time.strftime("%d%m%Y_%H%M")
initial_time = time.time()
#BNC 526 is at Cold Finger
filedirectory_526 = '/home/resonator/Desktop/Resonator_Voltage/526(Cold Finger)_'+run_time+'_keithley_DMM.csv'
#BNC 529 is inside the heat shield
filedirectory_529 = '/home/resonator/Desktop/Resonator_Voltage/529(Inside Heat Shield)_'+run_time+'_keithley_DMM.csv'

filedirectory_527 = '/home/resonator/Desktop/Resonator_Voltage/527_'+run_time+'_keithley_DMM.csv'
filedirectory_528 = '/home/resonator/Desktop/Resonator_Voltage/528_'+run_time+'_keithley_DMM.csv'

file_526 = open(filedirectory_526,"wb")
fcsv_526 = csv.writer(file_526,lineterminator="\n")
fcsv_526.writerow(["ElapsedTime(minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"])
file_526.close()

file_527 = open(filedirectory_527,"wb")
fcsv_527 = csv.writer(file_527,lineterminator="\n")
fcsv_527.writerow(["ElapsedTime(minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"])
file_527.close()

file_528 = open(filedirectory_528,"wb")
fcsv_528 = csv.writer(file_528,lineterminator="\n")
fcsv_528.writerow(["ElapsedTime(minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"])
file_528.close()

file_529 = open(filedirectory_529,"wb")
fcsv_529 = csv.writer(file_529,lineterminator="\n")
fcsv_529.writerow(["ElapsedTime(minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"])
file_529.close()
    
vc = VC()
while(1):
    file_526=open(filedirectory_526,"ab")
    fcsv_526=csv.writer(file_526,lineterminator="\n")
    voltage = keithley.get_dc_volts()
    tempK=vc.conversion(voltage+0.00369)
    elapsed_time_526 = (time.time() - initial_time)/60
    fcsv_526.writerow([elapsed_time_526, time.strftime("%H"+":"+"%M"), voltage, tempK])
    file_526.close()
    time.sleep(15)
    
    file_529 = open(filedirectory_529,"ab")
    fcsv_529 = csv.writer(file_529,lineterminator="\n")
    voltage = keithley.get_dc_volts()
    tempK = vc.conversion(voltage+0.00272)
    elapsed_time_529 = (time.time() - initial_time)/60
    fcsv_529.writerow([elapsed_time_529, time.strftime("%H"+":"+"%M"), voltage, tempK])
    file_529.close()
    time.sleep(15)
    
    file_527=open(filedirectory_527,"ab")
    fcsv_527=csv.writer(file_527,lineterminator="\n")
    voltage = keithley.get_dc_volts()
    tempK=vc.conversion(voltage+0.00369)
    elapsed_time_527 = (time.time() - initial_time)/60
    fcsv_527.writerow([elapsed_time_527, time.strftime("%H"+":"+"%M"), voltage, tempK])
    file_527.close()
    time.sleep(15)
    
    file_528=open(filedirectory_528,"ab")
    fcsv_528=csv.writer(file_528,lineterminator="\n")
    voltage = keithley.get_dc_volts()
    tempK=vc.conversion(voltage+0.00369)
    elapsed_time_528 = (time.time() - initial_time)/60
    fcsv_528.writerow([elapsed_time_528, time.strftime("%H"+":"+"%M"), voltage, tempK])
    file_528.close()
    time.sleep(15)
    
    
