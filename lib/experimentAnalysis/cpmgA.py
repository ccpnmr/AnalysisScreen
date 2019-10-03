from ccpn.core.lib.AssignmentLib import _assignNmrAtomsToPeaks
from ccpn.core.lib.ContextManagers import undoBlock,notificationEchoBlocking, undoBlockWithoutSideBar
import numpy as np
from scipy.stats import linregress

with undoBlock():
    with notificationEchoBlocking():
        sg = project.spectrumGroups[-2]
        nc = c = project.fetchNmrChain(sg.name)
        spectra =  sg.spectra
        iiLL = []
        for sp in spectra:
            il = sp.newIntegralList()
            ii = il.automaticIntegral1D()
            iiLL.append(ii)
        if len(iiLL)>0:
            # take first I list and set the limits of search
            foundMatches = {}
            for i in iiLL[0]:
                foundMatches.update({i:[]})
                limit = i.limits[-1]
                # limitsFirstSpectrum.append(limit)
                #loop over all other integrals and find integral mean limits  is within the range of the first spectrum limits
                for otherIntegList in iiLL[1:]:
                    for otherInteg in otherIntegList:
                        centerInt =  np.mean(otherInteg.limits[-1])
                        miL, maL = min(limit), max(limit)
                        if float(centerInt) >= float(miL) and float(centerInt) <= float(maL):
                            foundMatches.get(i).append(otherInteg)
            #  merge keys-values so to have a list of list
            foundll = [[i]+foundMatches[i] for i in foundMatches.keys()]
            # create peak for each region and assign to the integral

            for count, inGroup in enumerate(foundll):

                if len(inGroup) == len(spectra):
                    nr = nc.fetchNmrResidue(str(count))
                    neededNewPeakList = True
                    for inte in inGroup:
                        neededNewPeakList = True
                        na = nr.fetchNmrAtom('H')
                        sp = inte.integralList.spectrum
                        # if neededNewPeakList:
                        #     pl = sp.newPeakList()
                        # else:
                        pl = sp.peakLists[-1]
                        b, x, y = inte._1Dregions
                        height = np.max(y).astype(float)
                        bools = y == height
                        position = x[bools]
                        p = pl.newPeak(ppmPositions=[position[-1].astype(float), ], height=float(height))
                        inte.peak = p
                        p.volume = inte.value
                        _assignNmrAtomsToPeaks([p], [na])
                else:
                    print('Integrals count different from Spectra count. Skipped for now')


with undoBlock():
    with notificationEchoBlocking():
        ps = []
        sg  =  current.integrals[0].integralList.spectrum.spectrumGroups[-1]
        nc  =  c = project.fetchNmrChain(sg.name)
        nr  = nc.fetchNmrResidue('1')
        na  = nr.fetchNmrAtom('H')
        for i in current.integrals:
            sp  = i.integralList.spectrum
            pl = sp.newPeakList()
            b, x, y = i._1Dregions
            position = np.mean(x).astype(float)
            height  =  np.max(y).astype(float)
            p = pl.newPeak(ppmPositions=[position,], height=float(height))
            i.peak = p
            p.volume = i.value
            ps.append(p)
            _assignNmrAtomsToPeaks([p], [na])
            current.peaks = ps




SF = {}
for i in current.integrals:
    b,x,Y = i._1Dregions
    Y.sort()
    X = np.arange(len(Y))
    slope, intercept, r_value, p_value, std_err = linregress(X,Y)
    SF.update({i.integralList.spectrum.pid:slope})

sg = project.getByPid('SG:SF_H')
limits = (5.1924626349617871, 9.6461923150701221)
with undoBlockWithoutSideBar():
    with notificationEchoBlocking():
        for sp in sg.spectra:
            il = sp.newIntegralList()
            i = il.newIntegral()
            i.limits = limits

