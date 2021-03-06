#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2019"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:25 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.0 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 17, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from ccpn.AnalysisScreen.lib.experimentAnalysis.MatchPositions import matchPeaks


INCREASED = 'Increased'
DECREASED = 'Decreased'
BELOWTRESHOLD = 'Below threshold'


def _getPeaksObj(spectrum, peakListIndex=0):
    '''
    :param spectrum:
    :param peakListIndex:  peakList index
    :return: list of ccpn  peaks
    '''
    peaks = []
    if len(spectrum.peakLists) >= peakListIndex:
        for peak in spectrum.peakLists[peakListIndex].peaks:
            peaks.append(peak)
    return peaks


# - compare area for the peak
# def comparePeakArea(areaA, areaB, minimalDiff):
#   '''
#
#   :param areaA: Reference peak Area -> float
#   :param areaB: Target peak Area -> float
#   :param minimalDiff: threshold of difference
#   :return: the diff of PeakB-PeakA if greater then minimalDiff
#   'that means that there has been a Broadening event of the area'
#   '''
#   if areaA is not None and areaB is not None:
#     diff = areaB - areaA
#     if abs(diff) >= minimalDiff:
#       if diff > 0:
#         return INCREASED, diff
#       else:
#         return DECREASED, diff
#   return BELOWTRESHOLD, 0

def comparePeakArea(areaA, areaB, minimalDiff):
    '''

    :param areaA: Reference peak Area -> float
    :param areaB: Target peak Area -> float
    :param minimalDiff: threshold of difference
    :return: the ratio of PeakB-PeakA if greater then minimalDiff
    'that means that there has been a Broadening event of the area'
    '''
    if areaA is not None and areaB is not None:
        diff = abs(areaB - areaA)
        ratio = diff / areaB

        if ratio >= minimalDiff:
            return ratio
        else:
            return 0.0
    return 0.0


def findBroadenedPeaks(controlSpectrum, targetSpectrum, minimalDiff=0.5, limitRange=0.01, targetPLIndex=1):
    '''
    :param spectrumA:  Reference spectrum  -> object
    :param spectrumB:  Target spectrum object -> object
    :param minimalDiff:  minimalDiff: threshold of difference for each peak to be considered a broadening -> float (0 to 1)
    :param limitRange: ppm range where to find a matching peak
    :param targetPLIndex : peakList with linewidhts
    :return: list of peaks who recorded a broadening event

    Ratio for broadening = abs(controlPeakArea - targetPeakArea) / targetPeakArea

    '''

    peakHits = []
    matches = matchPeaks(reference=controlSpectrum, spectrumB=targetSpectrum, limitRange=limitRange,
                         refPeakListIndex=targetPLIndex)
    for match in matches:
        referencePeak, targetPeak, pos = match
        if referencePeak.lineWidths and targetPeak.lineWidths is not None:
            # if len(referencePeak.lineWidths) > 0 and len(targetPeak.lineWidths) > 0:
            if referencePeak.volume and targetPeak.volume:
                value = comparePeakArea(referencePeak.volume, targetPeak.volume, minimalDiff)
                if value >= minimalDiff:
                    peakHits.append(match)

    return peakHits

# def matchHitToReference(spectrumHit, referenceSpectra, limitRange=0.01, peakListIndex=1):
#   '''
#
#   :param targetHitSpectrum: spectrum calculated as hit (peak linewhidths changed compared to its control)
#   :param referenceSpectra: list of reference spectra. Eg mixture or single reference spectrum
#   :return: matches of the hit peak to the references
#   '''
#
#   hits = []
#   if referenceSpectra:
#     for referenceSpectrum in referenceSpectra:
#       matches = matchPeaks(reference=referenceSpectrum, spectrumB=spectrumHit, limitRange=limitRange,
#                               peakListIndex=peakListIndex)
#       hits.append(matches)
#
#   return hits
