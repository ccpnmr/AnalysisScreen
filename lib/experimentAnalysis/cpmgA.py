from ccpn.core.lib.AssignmentLib import _assignNmrAtomsToPeaks
from ccpn.core.lib.ContextManagers import undoBlock,notificationEchoBlocking, undoBlockWithoutSideBar
import numpy as np
import pandas as pd
from scipy.stats import linregress
import time
from tqdm import tqdm

from ccpn.core.lib.peakUtils import getNmrResidueDeltas,_getKd, oneSiteBindingCurve, _fit1SiteBindCurve, _fitExpDecayCurve,\
                                    MODES, LINEWIDTHS, HEIGHT, POSITIONS, VOLUME, DefaultAtomWeights, H, N, OTHER, C, DISPLAYDATA, \
                                    getRawDataFrame, RAW, getNmrResiduePeakProperty, _getPeaksForNmrResidue
from ccpn.AnalysisScreen.lib.experimentAnalysis.r2CalcutationMethods import calculateFit, percentageChange
import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

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




# SF = {}
# for i in current.integrals:
#     b,x,Y = i._1Dregions
#     Y.sort()
#     X = np.arange(len(Y))
#     slope, intercept, r_value, p_value, std_err = linregress(X,Y)
#     SF.update({i.integralList.spectrum.pid:slope})

# Calculate auto integral etc....
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
def resetLists():
    with undoBlockWithoutSideBar():
        with notificationEchoBlocking():
    project.deleteObjects(*project.integralLists)
    project.deleteObjects(*project.peakLists)
    for sp in project.spectra:
        il = sp.newPeakList()
    for sp in project.spectra:
        il = sp.newIntegralList()

resetLists()
sgSF = project.getByPid('SG:SF_cpmg_1')
sgSP = project.getByPid('SG:SP_cpmg_1')
il = sgSF.spectra[0].integralLists[-1]
masterLimits, bM, bm = il.findLimits()
cpgmAnalysis(sgSF, masterLimits)
cpgmAnalysis(sgSP, masterLimits)

 ##########////////////////////////////////////////

# open  two csm module on GUI

moduleName = 'Chemical Shift Mapping:1' # The displayed CSM module name you want to get information from.
csmSF = mainWindow.moduleArea.modules[moduleName]
moduleName = 'Chemical Shift Mapping:2' # The displayed CSM module name you want to get information from.
csmSP = mainWindow.moduleArea.modules[moduleName]

dfSF= csmSF._getAllBindingCurvesDataFrameForChain()
dfSP= csmSP._getAllBindingCurvesDataFrameForChain()

df_SF_scaled = csmSF._getScaledBindingCurves(dfSF)
df_SP_scaled = csmSP._getScaledBindingCurves(dfSP)

xV =  [0,45,50,100,300,500,800]
df_SF_scaled.columns = xV
df_SP_scaled.columns = xV
dfSF.columns = xV
dfSP.columns = xV

changes_slope_exp = []
changes_Interc_exp = []
changes_R2 = []
positions = []

savePlot = True
pdf = None
SavePath = '/Users/luca/Desktop/DFCI/cpmg_development/bindingCurves/'
if savePlot:
    pdf = PdfPages(SavePath+'CPMG_1_.pdf')
    for i in tqdm(range(dfSF.shape[0])):
        nrPid = dfSF.iloc[i].to_frame().transpose().index[0]
        peaks = [p for p in nrPid.nmrAtoms[0].assignedPeaks]
        ppositions = [p.position[0] for p in peaks]
        v_df_SF = dfSF.iloc[i].to_frame().transpose()
        v_df_SP = dfSP.iloc[i].to_frame().transpose()
        ySF = v_df_SF.values.flatten(order='F')
        ySP = v_df_SP.values.flatten(order='F')
        x = np.array(dfSP.columns)
        xf, yf, xs, z, slope, interc, R2_rf, std_err = calculateFit(x, ySF, 'SF')
        xf_SP, yf_SP, xs_SP, z_SP, slope_SP, interc_SP, R2_rf_SP, std_err_SP = calculateFit(x, ySP, 'SP')

        changeSlope = percentageChange(slope, slope_SP)
        changeInt = percentageChange(interc, interc_SP)
        changeR2 = percentageChange(R2_rf, R2_rf_SP)
        positions.append(ppositions[0])
        changes_slope_exp.append(changeSlope)
        changes_Interc_exp.append(changeInt)
        changes_R2.append(changeR2)
        if savePlot:
            plt.figure(dpi=300)
            plt.plot(xf, yf, color='blue', linestyle='dashed', label='SF-fitted')
            plt.plot(xs, z,  'o', markerfacecolor='blue',  label='SF-observ')
            plt.plot(xf_SP, yf_SP, color='red', label='SP-fitted')
            plt.plot(xs_SP, z_SP,  '*', markerfacecolor='red', label='SP-observ')
            plt.legend(loc='upper right')
            plt.text(max(xs), 0.45, 'Slope SF %0.4f' % slope)
            plt.text(max(xs),0.44, 'Slope SP %0.4f'%slope_SP)
            plt.text(max(xs), 0.43, 'changeSlope %0.3f' % changeSlope)

            nr = peaks[0].assignedNmrAtoms[0][0].nmrResidue
            title = 'NmrResidue: %s. Position: %0.3f ' %(nr.sequenceCode,ppositions[0])
            plt.title(title)
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()
if pdf:
    pdf.close()

dfChanges = pd.DataFrame([changes_slope_exp,
                          changes_Interc_exp,
                          changes_R2],)
dfChanges = dfChanges.transpose()
dfChanges.columns = ['NL Fit Slopes Changes',
                     'NL Fit Intercept Changes',
                     'NL Fit R2 Changes']
dfChanges['position'] = positions
dfChanges.index = dfSF.index


if False:
    t = time.time().__round__().__str__()
    dfChanges.to_excel('/Users/luca/Desktop/DFCI/cpmg_development/bindingCurves/'+t+'.xlsx')



# macro delete create obj
project.deleteObjects(*project.integralLists)
project.deleteObjects(*project.peakLists)
for sp in project.spectra:
    il = sp.newPeakList()
for sp in project.spectra:
    il = sp.newIntegralList()

#  get peak heights from current
ps = []
for s in project.spectrumGroups[-2].spectra:
    for p in current.peaks:
        if p in s.peakLists[0].peaks:
            ps.append(p.height)