from numpy import array, amin, amax, average, empty, nan, nanmin, fabs, subtract, where, argmax, NAN
import math
from collections import defaultdict
from itertools import chain, combinations
from collections import OrderedDict
from ccpn.AnalysisScreen.lib.SimulatedAnnealing import randomDictMixtures, iterateAnnealing, getOverlappedCount, scoreMixture, calculateOverlapCount
from ccpn.util.Logging import getLogger
from ccpn.core.Spectrum import Spectrum
from ccpn.ui.gui.widgets.MessageDialog import _stoppableProgressBar
from ccpn.core.lib.ContextManagers import notificationEchoBlocking
from ccpn.core.lib.ContextManagers import undoBlockWithoutSideBar


def _initialiseMixtures(params):
    calculationMethod = _getCalculationMethod(params)
    simulatedAnnealingParm = _getSimulatedAnnealingParm(params)
    mode = _getMode(params)
    modeNumber = _getNumber(params)
    minimalDistance = _getMinimalDistance(params)
    spectra = _getSpectra(params)
    replaceMixtures = True  #_getReplace(params)
    peaksAreTopick = _getPeakPicking(params)
    factor = _getFactor(params)
    noiseLevel = _getNoiseLevel(params)
    pickFilter = _getFilter(params)
    pickFilterMode = _getFilterMode(params)
    ignoredRegions = _getIgnoredRegions(params)
    if len(spectra) > 0:
        with notificationEchoBlocking():
            print(simulatedAnnealingParm, mode, modeNumber, minimalDistance)
            project = _getProjectFromSpectrum(spectra[0])
            currentVirtualSamples = _getCurrentVirtualSamples(project)
            if peaksAreTopick:
                _pickPeaks(spectra, pickFilter, factor, pickFilterMode, ignoredRegions, noiseLevel)

            if replaceMixtures:
                _deleteMixtures(project, currentVirtualSamples)
                _generateMixtures(project, spectra, calculationMethod, simulatedAnnealingParm, mode, modeNumber, minimalDistance, )
            else:
                _generateMixtures(project, spectra, calculationMethod, simulatedAnnealingParm, mode, modeNumber, minimalDistance)
    else:
        getLogger().warning('No spectra found')
        return


def _getCalculationMethod(params):
    return params['calculationMethod']


def _getSimulatedAnnealingParm(params):
    return params['simulatedAnnealingParm']


def _getNoiseThreshold(params):
    return params['threshold']


def _getMode(params):
    return params['mode']


def _getNumber(params):
    return params['number']


def _getMinimalDistance(params):
    return params['minimalDistance']


def _getSpectra(params):
    return params['spectra']


# def _getReplace(params):
#   value = params['replace']
#   if value == 'Yes':
#     return True

def _getPeakPicking(params):
    value = params['peakPicking']
    if value == 'Automatic':
        return True


def _getFactor(params):
    return params['factor']


def _getNoiseLevel(params):
    value = params['noiseLevel']
    if value == 'Estimated':
        return 0
    else:
        noiseLevel = _getNoiseThreshold(params)
        return noiseLevel


def _getFilter(params):
    return params['filter']


def _getFilterMode(params):
    return params['filterMode']


def _getIgnoredRegions(params):
    return params['ignoredRegions']


def _getProjectFromSpectrum(spectrum):
    return spectrum.project


def _deleteMixtures(project, currentMixtures):
    if len(currentMixtures)>0:
        project.deleteObjects(*currentMixtures)



def _getCompounds(spectra):
    compounds = []
    peakLists = []
    for spectrum in spectra:
        if isinstance(spectrum, Spectrum):
            if len(spectrum.peakLists) > 0:
                peakLists.append(spectrum.peakLists[0])

    for peakList in peakLists:
        if peakList is not None:
            spectrum = peakList.spectrum
            if spectrum.referenceSubstance is not None:
                name = spectrum.referenceSubstance.name
            else:
                name = spectrum.name
            compound = [name, [peak.position[0] for peak in peakList.peaks]]
            compounds.append(compound)
    return compounds


def _generateMixtures(project, spectra, method, methodParam, mode, n, minDistance, minTotalScore=None):
    import time
    s = time.time()
    compounds = _getCompounds(spectra)
    startTemp, finalTemp, maxSteps, k, coolingMethod, nIterations = list(methodParam.values())

    mixturesNumber = _getMixturesNumber(len(spectra), mode, n)
    randomMixtures = randomDictMixtures('Mixture', compounds, mixturesNumber)
    if method == 'Simulated Annealing':
        mixtures = iterateAnnealing(randomMixtures, startTemp, finalTemp, maxSteps, k, coolingMethod, nIterations, minDistance, minTotalScore)
        _createSamples(project, mixtures, minDistance)
    e = time.time()
    print('Time: ', e-s)

def _getMixturesNumber(lenght, mode, n):
    if mode == 'Select number of Mixtures':
        return n
    else:
        return math.floor(lenght / n)


def _createSamples(project, mixtures, minDistance):
    msg = '(2/2) Creating Mixtures...'
    with undoBlockWithoutSideBar():
        for mixtureName, mixtureCompounds in _stoppableProgressBar(mixtures.items(), msg):
            sample = project.newSample(name=str(mixtureName))
            sample.isVirtual = True
            _setMixtureScores(mixtureCompounds, sample, minDistance)
            _setSampleComponentScores(sample, mixtureCompounds, minDistance)


def _setMixtureScores(mixtureCompounds, sample, minDist=0.01):
    sample.score = round(scoreMixture(mixtureCompounds, minDist), 3)
    sample.overlaps = getOverlappedCount(mixtureCompounds, minDist)


def _getMixtureFromSample(sample):
    mixtureName = str(sample.name)
    spectra = []
    for sampleComponent in sample.sampleComponents:
        spectrum = sampleComponent.substance.referenceSpectra[0]
        spectra.append(spectrum)
    return {mixtureName: _getCompounds(spectra)}


def _getMixturesFromVirtualSamples(virtualSamples):
    mixtures = {}
    for sample in virtualSamples:
        mixture = _getMixtureFromSample(sample)
        mixtures.update(mixture)

    return mixtures


def _getCurrentVirtualSamples(project):
    ''' gets all virtual samples from project and converts them to dictionary mixtures'''
    currentVirtualSamples = []
    for sample in project.samples:
        if sample.isVirtual:
            virtualSample = sample
            currentVirtualSamples.append(virtualSample)
    return currentVirtualSamples


def _pickPeaks(spectra, filter, factor, filterMode, ignoredRegions, noiseThreshold):
    for spectrum in _stoppableProgressBar(spectra, '(1/2) Picking Peaks...'):
        spectrum.peakLists[0].pickPeaks1dFiltered(size=filter, mode=filterMode, excludeRegions=ignoredRegions,
                                                  positiveNoiseThreshold=noiseThreshold, factor=factor)


def _setSampleComponentScores(sample, mixtureCompounds,  minDist=0.01):
    totalScore = 0
    for compound in mixtureCompounds:
        compoundName, compoundPeakList = compound
        newSampleComponent = sample._fetchSampleComponent(str(compoundName))
        compoundsToCompare = [c[1] for c in mixtureCompounds if c[0] != compoundName]
        overlaped = calculateOverlapCount(compoundPeakList, compoundsToCompare, minDist)

        if overlaped is None:
            newSampleComponent.score = 0

        else:
            try:
                score = len(overlaped) / len(compoundPeakList)
            except ZeroDivisionError:
                score = 0

            newSampleComponent.score = round(score, 2)
            totalScore += score
            newSampleComponent.overlaps = list(set(overlaped))

def _rescoreMixture(sample, minDist=0.01):
    spectra = [s.substance.referenceSpectra[0] for s in sample.sampleComponents]
    compounds = _getCompounds(spectra)
    _setMixtureScores(compounds, sample)
    _setSampleComponentScores(sample, compounds)
