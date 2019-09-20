# Speed test
"""
Creates a typical screening project:
spectra,
sample,
sampleComponents,
substances,
peakLists,
peaks,
integralLists,
integral,
assign integral to peak,
nmrAtoms,
assign nmrAtoms to peak

"""
import time
from ccpn.core.lib.AssignmentLib import _assignNmrAtomsToPeaks
from ccpn.util.decorators import profile
from ccpn.ui.gui.lib.MenuActions import _openItemObject
import numpy as np
import random

t = time.time()
application._increaseNotificationBlocking()
project.suspendNotification()

sg = project.newSpectrumGroup(str(t))
spectra = []
nc  =  project.nmrChains[-1]
sa = project.newSample()
for rr in range(1000):
    sp = project.createDummySpectrum(['H'])
    su = project.newSubstance(sp.name)
    su.referenceSpectra = [sp]
    sa.newSampleComponent(su.name)
    sp.positions = np.arange(-4,14, 0.001)
    sp.intensities = np.random.normal(size=sp.positions.shape)
    spectra.append(sp)
    pl = sp.peakLists[-1]
    il = sp.newIntegralList()
    nr = nc.fetchNmrResidue(str(rr))
    for j in range(30):
        i = il.newIntegral()
        pos = random.choice(sp.positions)
        p = pl.newPeak(ppmPositions=[pos,], height=sp.intensities[pos].astype(float))
        na  = nr.fetchNmrAtom('H')
        p.integral = i
        _assignNmrAtomsToPeaks([p], [na])
sg.spectra = spectra
project.resumeNotification()
tBuild = time.time()
print('Build objects',tBuild-t )
# Build Spectra 2011.227870941162

t = time.time()
_openItemObject(mainWindow, spectra)
tOpen = time.time()
print('Open Spectra',tOpen-t )

t = time.time()
for rr in range(10):
    project.spectra[rr].delete()
tdelete = time.time()
print('delete Spectra',tdelete-t )
# delete 10 Spectra 44.77506709098816


# ADD Spectrum 5.875883102416992