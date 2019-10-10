from ccpn.core.lib.AssignmentLib import _assignNmrAtomsToPeaks
from ccpn.core.lib.ContextManagers import undoBlock,notificationEchoBlocking, undoBlockWithoutSideBar
import numpy as np
import pandas as pd
from scipy.stats import linregress
from ccpn.core.lib.peakUtils import getNmrResidueDeltas,_getKd, oneSiteBindingCurve, _fit1SiteBindCurve, _fitExpDecayCurve,\
                                    MODES, LINEWIDTHS, HEIGHT, POSITIONS, VOLUME, DefaultAtomWeights, H, N, OTHER, C, DISPLAYDATA, \
                                    getRawDataFrame, RAW, getNmrResiduePeakProperty, _getPeaksForNmrResidue

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


def _integrateAndAssign(integralList, nc, masterLimits):
    il = integralList
    sp = il.spectrum
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
                height = 0
                # newIntegral.delete()
                # nr.delete()
                # continue  # don't make a peak and delete objs
            bools = y == height
            position = x[bools]
            p = pl.newPeak(ppmPositions=[position[-1].astype(float), ], height=float(height))
            newIntegral.peak = p
            p.volume = newIntegral.value
            na = nr.fetchNmrAtom('H')
            _assignNmrAtomsToPeaks([p], [na])


def cpgmAnalysis(sg, masterLimits):

    with undoBlockWithoutSideBar():
        with notificationEchoBlocking():
            nc = project.fetchNmrChain(sg.name+'_')
            for sp in sg.spectra:
                il = sp.integralLists[-1]
                _integrateAndAssign(il, nc, masterLimits)

#     /////
sgSF = project.getByPid('SG:SF_cpmg_1')
sgSP = project.getByPid('SG:SP_cpmg_1')
il = sgSF.spectra[0].integralLists[-1]
masterLimits, bM, bm = il.findLimits()
cpgmAnalysis(sgSF, masterLimits)
cpgmAnalysis(sgSP, masterLimits)



hhsp42 = []
for i in current.peaks:
    hhsp42.append(i.height)

sum(hhsp42)/sum(hhsf42)
 # 0.7477087141625922
# 0.7309698505143472

moduleName = 'Chemical Shift Mapping:1' # The displayed CSM module name you want to get information from.
csmSF = mainWindow.moduleArea.modules[moduleName]
moduleName = 'Chemical Shift Mapping:2' # The displayed CSM module name you want to get information from.
csmSP = mainWindow.moduleArea.modules[moduleName]

dfSF= csmSF._getAllBindingCurvesDataFrameForChain()
dfSP= csmSP._getAllBindingCurvesDataFrameForChain()

scaledSF = csmSF._getScaledBindingCurves(dfSF)
scaledSF.columns = [0,45,50,100,300,500,800]
for i in range(scaledSF.shape[0]):
    xsf, ysf, xff, yff, *poptf = _fitExpDecayCurve(scaledSF.iloc[i].to_frame().transpose())
    slope, intercept, r_value, p_value, std_err = linregress(xsf, ysf)
    slopef, interceptf, r_valuef, p_valuef, std_errf = linregress(xff, yff)

    print(poptf, 'slopes:', slope, slopef )


scaledSF = csmSF._getScaledBindingCurves(dfSF)
scaledSP = csmSP._getScaledBindingCurves(dfSP)
scaledSF.columns = [0,45,50,100,300,500,800]
scaledSP.columns = [0,45,50,100,300,500,800]

changes = []
linearChanges = []
positions = []
for i in range(scaledSF.shape[0]):
    nrPid = scaledSF.iloc[i].to_frame().transpose().index[0]

    peaks = [p for p in nrPid.nmrAtoms[0].assignedPeaks]
    ppositions = [p.position[0] for p in peaks]
    xsf, ysf, xff, yff, *poptf = _fitExpDecayCurve(scaledSF.iloc[i].to_frame().transpose())
    xsp, ysp, xfp, yfp, *poptp = _fitExpDecayCurve(scaledSP.iloc[i].to_frame().transpose())
    slope_f, intercept_f, r_value_f, p_value_f, std_err_f = linregress(xsf, ysf)
    slope_p, intercept_p, r_value_p, p_value_p, std_err_p = linregress(xsp, ysp)
    change = ((poptp[1] - poptf[1]) / abs(poptp[1])) * 100
    changeLinear = ((slope_p -slope_f) / abs(slope_p)) * 100
    changes.append(change)
    linearChanges.append(changeLinear)
    positions.append(ppositions[0])
dfChanges = pd.DataFrame([changes, linearChanges],)
dfChanges = dfChanges.transpose()
dfChanges.columns = ['nonLinear', 'linear']
dfChanges['position'] = positions
dfChanges.index = scaledSF.index
dfChanges.to_excel('/Users/luca/Desktop/DFCI/cpmg_development/bindingCurves/changes_Cpmg_1_PF_pos.xlsx')

def getFittedDf(scaledDf):
    dfs =[]
    for i in range(scaledDf.shape[0]):
        _df = scaledDf.iloc[i].to_frame().transpose()
        xsf, ysf, xff, yff, *popt = _fitExpDecayCurve(_df)
        newDf = pd.DataFrame(yff, index=scaledDf.index, columns=xff)
        newDf['interc'] = popt[0]
        newDf['slope'] = popt[1]
        dfs.append(newDf)
    return pd.concat(dfs)

project.deleteObjects(*project.integralLists)
project.deleteObjects(*project.peakLists)
for sp in project.spectra:
    il = sp.newPeakList()
for sp in project.spectra:
    il = sp.newIntegralList()


for i in current.strip.peakListViews:
    i.setVisible(False)
for i in current.strip.integralListViews:
    i.setVisible(False)