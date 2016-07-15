import labrad
import time
import datetime
import numpy as np

#print"Waiting 8 hours to start"

#time.sleep(8*3600)

SAVE_DATA = True

cxn = labrad.connect()

delta_f = 0.001
start_freq = 1.0
stop_freq = 18.0

pulse_duration = 1e4

no_of_meas = int((stop_freq-start_freq)/delta_f)
print no_of_meas
basename = 'c:/data_resonator/data_auto/'
today = datetime.date.today()
mean_name = 'Y:/resonator-cooling/Data/resonator_auto/'

mso = cxn.msox_server()
mso.select_device()
mso.setformat('BYTE')



#if SAVE_DATA:
#    tps.setrms()
rg = cxn.rigol_dg4062_server()
rg.select_device()



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
    lt = len(clntimestr)
    lv = len(clnvaluelist)
    #######
    if  lt != lv:
        print "mismatched data lengths:  time array {0}, value array {1}".format(lt, lv)
        while (len(clntimestr) > len(clnvaluelist)):
            clntimestr.pop()
        while (len(clntimestr) < len(clnvaluelist)):
            clnvaluelist.pop()
        print "lengths after shifting: time array {0}, value array {1}".format(len(clntimestr), len(clnvaluelist))
        #######
    outlist = []
    for x in range(len(clntimestr)):
        outlist.append([clntimestr[x],clnvaluelist[x]])
    outarray = np.array(outlist)
    m1 = np.sum(np.abs(outarray[1500:2000,1]))
    #print m1
    mean_list.append([freq,m1])
#    np.savetxt(filename, outarray, delimiter=",")
    np.save(filename,outarray)
    return mean_list

def get_rms(tps, mean_list, freq):
    m1 = float(tps.getvalue())
    mean_list.append([freq,m1])
    return mean_list


mean_list = []
for i in range(no_of_meas):
    t1 = time.time()
    freq = start_freq + i * delta_f
    print 'taking data at freq: ' + str(freq)
    ncycles = int(pulse_duration*freq)
    #print ncycles

    mso.singletrig()

    rg.burst_cycles(ncycles)
    rg.frequency(freq)
    rg.trigger()



    time.sleep(.3)
    filename = basename + str(freq) + '.csv'
    if SAVE_DATA:
        mean_list = get_data(mso, filename, mean_list, freq)
    else:
        mean_list = get_rms(mso,mean_list,freq)
    print 'time: ' + str(time.time()-t1)
    np.savetxt(mean_name + 'mean{:%y%m%d}.csv'.format(today), np.array(mean_list))
