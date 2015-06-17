import labrad
import time
import datetime
import numpy as np

SAVE_DATA = True

cxn = labrad.connect()

delta_f = 0.001
start_freq = 1.0
stop_freq = 20

pulse_duration = 1e3

no_of_meas = int((stop_freq-start_freq)/delta_f)
print no_of_meas
basename = 'c:/data_resonator/data_auto/'
today = datetime.date.today()
mean_name = 'Y:/resonator-cooling/Data/resonator_auto/'

tps = cxn.tektronixtds_server()
tps.select_device()
if SAVE_DATA:
    tps.setrms()
rg = cxn.rigol_dg4062_server()
rg.select_device()


def get_data(tps, filename, mean_list, freq):
    answer=tps.getcurve()
    outlist = []
    for x in range(len(answer)):
        outlist.append([answer[x][0],answer[x][1]])
    outarray = np.array(outlist)
    m1 = np.sum(np.abs(outarray[1500:2000,1]))
    #print m1
    mean_list.append([freq,m1])
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
    rg.burst_cycles(ncycles)
    rg.frequency(freq)
    rg.trigger()
    time.sleep(.3)
    filename = basename + str(freq) + '.csv'
    if SAVE_DATA:
        mean_list = get_data(tps, filename, mean_list, freq)
    else:
        mean_list = get_rms(tps,mean_list,freq)
    print 'time: ' + str(time.time()-t1)
    np.savetxt(mean_name + 'mean{:%y%m%d}.csv'.format(today), np.array(mean_list))