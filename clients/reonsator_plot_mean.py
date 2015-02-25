from pylab import *
import numpy as np

mean_dir = 'Y:/resonator-cooling/Data/resonator_auto/'
fname = "mean150217.csv"

a = np.loadtxt(mean_dir + fname)
figure()
plot(a[:,0],a[:,1])
show()
