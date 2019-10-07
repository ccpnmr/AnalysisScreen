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

#     /////
sgSF = project.getByPid('SG:SF_cpmg_1')
sgSP = project.getByPid('SG:SP_cpmg_1')
# for sp in sg.spectra:
#     il = sp.newIntegralList()
il = sg.spectra[0].integralLists[-1]
masterLimits, bM, bm = il.findLimits()
with undoBlockWithoutSideBar():
    with notificationEchoBlocking():
        nc  = project.fetchNmrChain(sg.name)
        for sp in sg.spectra:

            il = sp.integralLists[-1]
            for count, limits in enumerate(masterLimits):
                nr = nc.fetchNmrResidue(str(count))
                minI, maxI = min(limits), max(limits)
                lineWidth = abs(maxI - minI)
                if lineWidth:
                    newIntegral = il.newIntegral(value=None, limits=[[minI, maxI], ])
                    newIntegral._baseline = bM
                    pl = sp.peakLists[-1]
                    b, x, y = newIntegral._1Dregions
                    try:
                        height = np.max(y).astype(float)
                    except:
                        newIntegral.delete()
                        nr.delete()
                        continue # don't make a peak and delete objs
                    bools = y == height
                    position = x[bools]
                    p = pl.newPeak(ppmPositions=[position[-1].astype(float), ], height=float(height))
                    newIntegral.peak = p
                    p.volume = newIntegral.value
                    na = nr.fetchNmrAtom('H')
                    _assignNmrAtomsToPeaks([p], [na])


sg = project.getByPid('SG:References')
shift = 0.111
for sp in sg.spectra:
    sp.positions += shift


hhsp42 = []

for i in current.peaks:
    hhsp42.append(i.height)

sum(hhsp42)/sum(hhsf42)
 # 0.7477087141625922
# 0.7309698505143472