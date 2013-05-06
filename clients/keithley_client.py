import labrad
import numpy
import time
from voltage_conversion import voltage_conversion as VC
import csv

def main():
    cxn = labrad.connect()
    keithley = cxn.keithley_2100_dmm()
    keithley.select_device()

    cxnpulser = yield connectAsync('192.168.169.29')
    pulser = cxnpulser.pulser()
    #Initially switch off the TTL pulse.
    pulser.switch_manual("Thermometer", False)

    run_time = time.strftime("%d%m%Y_%H%M")
    initial_time = time.time()
    #BNC 526 is at Cold Finger
    filedirectory_526 ='c:/data_resonator_voltage/526(Cold Finger)_keithley_DMM_'+run_time+'.csv'
    #BNC 529 is inside the heat shield
    filedirectory_529 ='c:/data_resonator_voltage/529(Inside Heat Shield)_keithley_DMM_'+run_time+'.csv'

    file_526 = open(filedirectory_526,"wb")
    fcsv_526 = csv.writer(file_526,lineterminator="\n")
    fcsv_526.writerow(["ElapsedTime_(minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"])
    file_526.close()

    file_529 = open(filedirectory_529,"wb")
    fcsv_529 = csv.writer(file_529,lineterminator="\n")
    fcsv_529.writerow(["ElapsedTime_(minutes)", "CurrentTime(H:M)", "Voltage(V)", "Temperature(K)"])
    file_529.close()

    vc = VC()

    # Inverter's 1A is connected to COM1(BNC 526)'s logic, and 1Y is connected to COM2(BNC 529)'s logic,
    # so when we want to measure 526 -> pulse.switch_manual("Thermometer", False): IN1 = LOW / IN2 = HIGH
    # and when we measure 529 -> pulse.switch_manual("Thermometer", True): IN1 = HIGH / IN2 = LOW
    # Switch is normally closed, so when we apply the HIGH logic, it will measure the voltage. 
    
    while(1):
        file_526=open(filedirectory_526,"ab")
        fcsv_526=csv.writer(file_526,lineterminator="\n")
        voltage = keithley.get_dc_volts()
        tempK=vc.conversion(voltage)
        elapsed_time_526 = (time.time() - initial_time)/60
        fcsv_526.writerow([elapsed_time_526, time.strftime("%H"+":"+"%M"), voltage, tempK])
        file_526.close()
        pulser.switch_manual("Thermometer", True)
        time.sleep(30)
    
        file_529 = open(filedirectory_529,"ab")
        fcsv_529 = csv.writer(file_529,lineterminator="\n")
        pulser.Start_Single()
        voltage = keithley.get_dc_volts()
        tempK = vc.conversion(voltage)
        elapsed_time_529 = (time.time() - initial_time)/60
        fcsv_529.writerow([elapsed_time_529, time.strftime("%H"+":"+"%M"), voltage, tempK])
        file_529.close()
        pulser.switch_manual("Thermometer", False)
        time.sleep(30)
