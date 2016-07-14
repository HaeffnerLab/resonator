import labrad

cxn = labrad.connection()
ps = cxn.keithley_2220_30_1()
ps.select_device()

a = ps.voltage()
