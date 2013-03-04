import labrad
import numpy
import time
import voltage_conversion as cF

cxn = labrad.connect()
kdmm = cxn.Keithley_2100 _DMM()

while(1):
    voltage=[]
    tempK=[]
    voltage_array = kdmm.getdcVolts().asarray
    voltage.append(kdmm.getdcVolts())
    tempK_array= cF.converter(kdmm.getdcVolts()).asarray
    tempK.append(cF.converter(kdmm.getdcVolts())
    filename="C:/Documents/Desktop/Data_DMM/Voltage vs Temperature.csv"
    numpy.savetxt(filename,tempK)
    #time.sleep(60)
