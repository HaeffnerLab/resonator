import labrad
import time

cxn_dmm = labrad.connect("192.168.169.30") #Connect to Camera computer, which includes Keithley digital multimeter (dmm)
dmmServer = cxn_dmm.keithley_2110_dmm() #connect to Keithley server, known as dmmServer

cxn_pulser = labrad.connect() #Connect to labrad manager on this computer
pulserServer = cxn_pulser.pulser() #Connect to pulser server, known as pulser

Num_Outputs = 22 #Number of DC electrodes
DC_Voltages = list() #An empty (to be populated) list of electrode voltages

#Sends a square pulse of time t
def sendPulse(t):
    pulserServer.switch_manual('DC multiplexer', True)
    time.sleep(t)
    pulserServer.switch_manual('DC multiplexer', False)
    time.sleep(t)

for i in range(Num_Outputs):
    sendPulse(0.01)    #Send a pulse, triggering the microcontroller to output the next voltage
    voltage = dmmServer.get_dc_volts()  #get the voltage from the Keithley
    DC_Voltages.append(voltage)    #append it to the list DC_Voltages
    
print DC_Voltages