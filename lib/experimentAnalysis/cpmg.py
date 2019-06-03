# Start as macro

'''

create nmrChain for each substance
same names
link spectrum to substance
for each peak in spectrum
add 1 nmrResidue and one atom as the peak axisCode



'''

for n, s in enumerate(project.substances):
    c = project.fetchNmrChain(s.name)

sample = project.samples[0]
sample.spectra = project.spectra
nmrChain = project.fetchNmrChain(sample.name)

for spectrum in sample.spectra:
    for n, peak in enumerate(spectrum.peakLists[-1].peaks):
        nmrResidue = nmrChain.fetchNmrResidue(str(n))
        for axisCode in peak.axisCodes:
            nmrAtom = nmrResidue.fetchNmrAtom(axisCode)
            peak.assignDimension(axisCode, nmrAtom)



# get data
from ccpn.core.lib.peakUtils import getSpectrumData
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
from mpl_toolkits import mplot3d
from ccpn.util.Common import getAxisCodeMatchIndices, getAxisCodeMatch
from ccpn.ui.gui.lib.GuiSpectrumViewNd import _getLevels

from scipy.stats import linregress

rr = []
for i, p in enumerate(project.peaks):
    s = p.peakList.spectrum
    data, b, c, d = getSpectrumData(p, 10)
    y = sorted(data, reverse=True)
    x = np.arange(b[0][0], b[1][0])
    reg = linregress(x, y)
    rr.append(reg.slope)
    plt.plot(y)
    print(i, reg.slope)
plt.show()

plt.plot(rr)
plt.show()