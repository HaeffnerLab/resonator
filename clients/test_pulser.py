import labrad
import time

cxn = labrad.connectAsync('192.168.169.29')
pulse = cxn.pulser()

count = 0 
while (count <= 10):
  pulse.switch_manual("11",True)
  sleep(5)
  pulse.switch_manual("11",False)
  sleep(5)
  count += 1
  
