from __future__ import division
import matplotlib

from matplotlib import pyplot
import qutip as q
import numpy as np
import labrad

'''
this analyzes the tomography experiment on April 02, 2013 where we compare (a) tomography at the dephasing time with no dephasing
and (b) tomography at the dephasing time after the dephasing. The results are the same, showing no coherence
(as it must be due to frequency switching) and therefore we are dephasing in the right basis.
'''
trials = 100
date = '2013Apr02'
#before dephasing
#folders = ['2258_22','2258_28','2258_34','2258_41','2258_47','2258_53','2258_59','2259_06','2259_12','2259_18']
#afted dephasing
folders = ['2259_58','2300_04','2300_10','2300_16','2300_23','2300_29','2300_35','2301_25','2301_31','2301_37']
results = np.zeros((len(folders), 3))
cxn = labrad.connect()
dv = cxn.data_vault
for i,folder in enumerate(folders):
    dv.cd(['', 'Experiments','RamseyDephaseTomography', date, folder])
    dv.open(1)
    measurement = dv.get().asarray
    results[i] = measurement.transpose()[1]
p1,p2,p3 = np.average(results, axis = 0)

z = p1
y = p2 - 1/2
x = 1/2 - p3

density_matrx = np.array([[z, x + 1j*y],[x - 1j*y, 1 - z]])

real = np.real(density_matrx)
imag = np.imag(density_matrx)

#make the figure
#this uses the qutip routine as the baseline but then makes modifications for bigger font sizes
fig = pyplot.figure()

labels = ['|D>','|S>']
zlim = [-1,1]
norm = matplotlib.colors.Normalize(zlim[0], zlim[1])
#first plot
ax = fig.add_subplot(121, projection = '3d')
ax.set_title('Real', fontsize = 30)
q.matrix_histogram(real,  limits = zlim, fig = fig, ax = ax, colorbar = False)
ax.set_xticklabels(labels, fontsize = 22)
ax.set_yticklabels(labels, fontsize = 22)
ax.tick_params(axis='z', labelsize=22)
cax, kw = matplotlib.colorbar.make_axes(ax, shrink=.75, pad=.0)
cb1 = matplotlib.colorbar.ColorbarBase(cax, norm = norm)
cl = pyplot.getp(cax, 'ymajorticklabels') 
pyplot.setp(cl, fontsize=22)
#next subplot
ax = fig.add_subplot(122, projection = '3d')
ax.set_title('Imaginary', fontsize = 30)
q.matrix_histogram(imag, limits = zlim, fig = fig, ax = ax, colorbar = False)
ax.set_xticklabels(labels, fontsize = 22)
ax.set_yticklabels(labels, fontsize = 22)
ax.tick_params(axis='z', labelsize=22)
cax, kw = matplotlib.colorbar.make_axes(ax, shrink=.75, pad=.0)
cb1 = matplotlib.colorbar.ColorbarBase(cax, norm = norm)
cl = pyplot.getp(cax, 'ymajorticklabels') 
pyplot.setp(cl, fontsize=22)


#ax = fig.add_subplot(133)
#ax.get_xaxis().set_visible(False)
#ax.get_yaxis().set_visible(False)

#def errorBarSimple(trials, prob):
#    #look at wiki http://en.wikipedia.org/wiki/Checking_whether_a_coin_is_fair
#    '''returns 1 sigma error bar on each side i.e 1 sigma interval is val - err < val + err'''
#    Z = 1.0
#    s = np.sqrt(prob * (1.0 - prob) / float(trials))
#    err = Z * s
#    return err
#
#err = errorBarSimple
#
#
#error_matrix = np.array(
#                        [
#                         [err(trials, p1), err(trials,p3) + 1.j * err(trials, p2)],
#                         [err(trials,p3) - 1.j * err(trials,p2), err(trials,p1)]
#                         ]
#                        )
#error_matrix = np.round(error_matrix, 2)

#ax.annotate("Measurement", xy=(0.2, 0.8), fontsize = 20, xycoords="axes fraction")
#ax.annotate(density_matrx, xy=(0.2, 0.7), fontsize = 20, xycoords="axes fraction")
#ax.annotate(" 'Error Bar' ", xy=(0.2, 0.6), fontsize = 20, xycoords="axes fraction")
#ax.annotate(error_matrix, xy=(0.2, 0.5), fontsize = 20, xycoords="axes fraction")
pyplot.show()