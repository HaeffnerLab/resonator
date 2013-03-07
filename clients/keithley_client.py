import labrad
import numpy
import time
import voltage_conversion
VC=voltage_conversion()

cxn = labrad.connect()
kdmm = cxn.Keithley_2100 _DMM()



filename='c:/data_resonator/keithley_DMM_'+time.strftime("%d%m%Y_%H%M")+'.csv'
numpy.savetxt(filename,time.strftime("%H%M"),voltage,tempK)
f.open(filename,"w")

while(1):
    optstr=""
    voltage_array = kdmm.getdcVolts().asarray
    tempK_array= VC.converter(kdmm.getdcVolts()).asarray
    optstr+= str(time.strftime("%H%M")) + " "
    optstr+= str(kdmm.getdcVolts()) + " "
    oprstr+=str(VC.converter(kdmm.getdcVolts()))+"\n"
    #time.sleep(60)
    
f.write(optstr)
f.close()
    