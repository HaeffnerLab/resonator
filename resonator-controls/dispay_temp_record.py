import numpy as np
import matplotlib.pyplot as plt
import sys


"""Load temp data saved by temp_record.py and plot it"""

strings = sys.argv

if len(strings) < 2:
    print "need to specify a filename"
    exit(-1)

fname = strings[1]

d = np.loadtxt(fname)
t = d[:, 0]/3600.0
temp = d[:, 1]

plt.plot(t, temp, '-o')
plt.grid(True)
plt.xlabel('time, hrs')
plt.ylabel('temp, K')
plt.title(fname)
plt.show()
