import labrad
import numpy
import time
import labrad.units as U
WithUnit = U.WithUnit

cxn = labrad.connect('192.168.169.29')
cameracomputercxn = labrad.connect()
marconi = cameracomputercxn.marconi_server()
tds = cameracomputercxn.tektronixtds_server()
tds.select_device()

#
#
#
# change frequency step size when there is less noise

f=marconi.frequency() #in MHz set frequency
print f
prev = tds.getvalue()     #previous pk2pk value in volts
print prev
f=marconi.frequency(f+0.1) #change f +.01

while (True):
    curr = tds.getvalue() #current pk2pk value in Volts

    
    if curr>prev:
        print 'case 1'
        prev=curr                   #set previous pk2pk to current pk2pk
        f=marconi.frequency(f+0.1) #change f +.01
    elif curr<prev:
        print 'case 2'
        f=marconi.frequency(f-0.2) #change f -.02
        actual=tds.getvalue()
        if actual<prev:
            print f
            print prev; print 'V'
            break
        #else:
            #curr=prev
        
    else:
        print 'case 3'
        print f; print 'best frequency MHz'
        print curr
        break

