import labrad
import numpy as np
import time
import datetime

cxn = labrad.connect()
mso = cxn.msox_server()
mso.select_device()

# mso.setformat('ASCII')
# mso.setpoints(31250)
# print 'points {}'.format(mso.getpoints())
# data = mso.getraw()
# listdata = list(data)
# # valuelist = []
# # for x in listdata:
# #     valuelist.append(ord(x))
# timestr = mso.gettimestr()
# # ymulti=mso.getYmulti()
# # origin = mso.getyorigin()
# # yref = mso.readYref()
# # truvaluelist = [(x-yref)*ymulti+origin for x in valuelist]
#
# clntimestr = [timestr[x].value for x in range(len(timestr))]
# clnvaluelist = [data[x] for x in range(len(data))]
# print np.array((clntimestr,clnvaluelist))
# print np.array(clnvaluelist)

basename = 'c:/data_resonator/data_auto/'
today = datetime.date.today()
mean_name = 'Y:/resonator-cooling/Data/resonator_auto/'

mso = cxn.msox_server()
mso.select_device()
mso.setformat('BYTE')

def get_data(tps, filename, mean_list, freq):
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
    m1 = np.sum(np.abs(outarray[1500:2000,1]))
    #print m1
    mean_list.append([freq,m1])
#    np.savetxt(filename, outarray, delimiter=",")
    print outarray
    np.save(filename,outarray)
    return mean_list

freq = 111
mean_list = []
filename = basename+'test_paddle_right1_held2.csv'
mean_list = get_data(mso, filename, mean_list, freq)