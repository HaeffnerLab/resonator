__author__ = 'experimenter'
import labrad
import numpy as np
import time

cxn = labrad.connect()
mso = cxn.msox_server()
mso.select_device()
mso.setformat('BYTE')


while(1):
    optstr=raw_input('taking data on pressing return, enter string to be added to filename:\n')
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
    outlist = []
    for x in range(len(clntimestr)):
        outlist.append([clntimestr[x],clnvaluelist[x]])
    outarray = np.array(outlist)
    filename='c:/data_resonator/curve_osci_'+time.strftime("%d%m%Y_%H%M_")+optstr+'.csv'
    np.save(filename,outarray)