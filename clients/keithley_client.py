import labrad
import time
from voltage_conversion import voltage_conversion as VC
import csv

#Run on the Linux
cxn = labrad.connect()
pulser = cxn.pulser()
#Initially switch off the TTL pulse
pulser.switch_manual('Thermometer', True)
#Connect to Windows Computer to use Keithley DMM
cxndmm = labrad.connect('192.168.169.30')
keithley = cxndmm.keithley_2100_dmm()
keithley.select_device()

run_time = time.strftime("%d%m%Y_%H%M")
initial_time = time.time()
#BNC 526 is at Cold Finger
filedirectory_526 = '/home/resonator/Desktop/Resonator_Voltage/526(Cold Finger)_'+run_time+'_keithley_DMM.csv'
#BNC 529 is inside the heat shield
filedirectory_529 = '/home/resonator/Desktop/Resonator_Voltage/529(Inside Heat Shield)_'+run_time+'_keithley_DMM.csv'

file_526 = open(filedirectory_526,"wb")
fcsv_526 = csv.writer(file_526,lineterminator="\n")
fcsv_526.writerow(["ElapsedTime(minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"])
file_526.close()

file_529 = open(filedirectory_529,"wb")
fcsv_529 = csv.writer(file_529,lineterminator="\n")
fcsv_529.writerow(["ElapsedTime(minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"])
file_529.close()

vc = VC()
while(1):
    file_526=open(filedirectory_526,"ab")
    fcsv_526=csv.writer(file_526,lineterminator="\n")
    voltage = keithley.get_dc_volts()
    tempK=vc.conversion(voltage)
    elapsed_time_526 = (time.time() - initial_time)/60
    fcsv_526.writerow([elapsed_time_526, time.strftime("%H"+":"+"%M"), voltage, tempK])
    file_526.close()
    pulser.switch_manual('Thermometer', False)
    time.sleep(30)
    
    file_529 = open(filedirectory_529,"ab")
    fcsv_529 = csv.writer(file_529,lineterminator="\n")
    voltage = keithley.get_dc_volts()
    tempK = vc.conversion(voltage)
    elapsed_time_529 = (time.time() - initial_time)/60
    fcsv_529.writerow([elapsed_time_529, time.strftime("%H"+":"+"%M"), voltage, tempK])
    file_529.close()
    pulser.switch_manual('Thermometer', Truesssss)
    time.sleep(30)
