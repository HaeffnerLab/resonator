import labrad
import numpy as np
import time

cxn = labrad.connect()
mso = cxn.msox_server()
mso.select_device()

mso.setformat('BYTE')
mso.setpoints(31250)
print 'points {}'.format(mso.getpoints())
data = mso.getraw()
listdata = list(data)
valuelist = []
for x in listdata:
    valuelist.append(ord(x))
timestr = mso.gettimestr()
ymulti=mso.getYmulti()
origin = mso.getyorigin()
yref = mso.readYref()
truvaluelist = [(x-yref)*ymulti+origin for x in valuelist]

clntimestr = [timestr[x].value for x in range(len(timestr))]
clnvaluelist = [truvaluelist[x].value for x in range(len(truvaluelist))]
print np.array((clntimestr,clnvaluelist))
print np.array(clnvaluelist)