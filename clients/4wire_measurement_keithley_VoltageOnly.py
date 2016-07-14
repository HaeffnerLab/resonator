
import labrad
from time import *
from csv import *
import numpy as np
from keithley_helper import voltage_conversion as VC
from keithley_helper import resistance_conversion as RC

#Run on the Windows
cxn = labrad.connect()
#Connect to Windows Computer to use Keithley DMM

keithley2 = cxn.keithley_2100_dmm()
keithley = cxn.keithley_2110_dmm()

keithley.select_device()
keithley2.select_device()
#load calibraton files and get ready for temperaturelookup
V529 = np.loadtxt('calibration files/529(Inside Heat Shield)_28062013_1107_keithley_DMM.csv',delimiter=',')
V529 = V529.transpose()

TempV529=V529[3][::-1]
VoltV529=V529[2][::-1]


run_time = strftime("%d%m%Y_%H%M")
initial_time = time()
#BNC 526 is at Cold Finger
#filedirectory_526 = '/home/resonator/Desktop/Resonator_Voltage/526(Cold Finger)_'+run_time+'_keithley_DMM.csv'
filedirectory_526 = 'Y:/resonator-cooling/Data/resonator_auto/4WMvoltagevstemperature_'+run_time+'_keithley_DMM.csv'


# Each colum headers is the following:
#["Elapsed Time (minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"

vc = VC()
rc = RC()
while(1):
#    pulser.switch_manual('Cold Finger', True)
    file_526 = open(filedirectory_526,"ab")
    fcsv_526 = writer(file_526,lineterminator="\n")
    voltage = keithley2.get_dc_volts()
    temp = vc.conversion(voltage)
    resistor_voltage = keithley.get_dc_volts()
    elapsed_time_526 = (time() - initial_time)/60
    fcsv_526.writerow([round(elapsed_time_526,4), strftime("%H"+"%M"), voltage, round(temp, 3), resistor_voltage])
    file_526.close()
    print temp
    print resistor_voltage
    sleep(1)
