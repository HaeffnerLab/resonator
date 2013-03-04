import labrad
import numpy
import time
import voltage_conversion as cF

cxn = labrad.connect()
kdmm = cxn.Keithley_2100 _DMM()



filename='c:/data_resonator/keithley_DMM_'+time.strftime("%d%m%Y_%H%M")+'.csv'
numpy.savetxt(filename,time.strftime("%H%M"),voltage,tempK)

while(1):
    voltage=[]
    tempK=[]
    voltage_array = kdmm.getdcVolts().asarray
    #voltage.append(kdmm.getdcVolts())
    tempK_array= cF.converter(kdmm.getdcVolts()).asarray
    #tempK.append(cF.converter(kdmm.getdcVolts())
    #time.sleep(60)
    
f.open(filename,"w")
f.write("%d%m%Y_%H%M",voltage_array,tempK_array)
f.close()
    