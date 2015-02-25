import labrad
import numpy
import time

cxn = labrad.connect()
tps = cxn.tektronixtds_server()
tps.select_device()
tps.setpk2pk()

while(1):
    currentv = tps.getvalue()
    currentt = time.strftime("%d%m%Y_%H%M_")