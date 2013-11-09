import labrad
import numpy
import time
import labrad.units as U
WithUnit = U.WithUnit

cxn = labrad.connect('192.168.169.29')
cameracomputercxn = labrad.connect()
marconi = cxn.marconi_server()
tds = cameracomputercxn.tektronixtds_server()
tds.select_device()


x = tds.returnvalue()
y = #current best amplitude

for i in range(100):
    f=marconi.frequency()
    if y<x:
        f+#some integer
        #store new f
    elif y>x:
        f-#some integer
        #store new f
    else:
        print #new f
        print 'is current best'
        quit 
