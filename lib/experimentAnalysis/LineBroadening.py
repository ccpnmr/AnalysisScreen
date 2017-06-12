#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
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
def comparePeakArea(areaA, areaB, minimalDiff):
  '''

  :param areaA: Reference peak Area -> float
  :param areaB: Target peak Area -> float
  :param minimalDiff: threshold of difference
  :return: the diff of PeakB-PeakA if greater then minimalDiff
  'that means that there has been a Broadening event of the area'
  '''

  diff = areaB - areaA
  if abs(diff) >= minimalDiff:
    if diff > 0:
      return INCREASED, diff
    else:
      return DECREASED, diff
  return BELOWTRESHOLD, 0


def findBroadenedPeaks(ReferenceSpectrum, targetSpectrum, minimalDiff=0.01, limitRange=0.01, peakListIndex=1):
  '''
  :param spectrumA:  Reference spectrum  -> object
  :param spectrumB:  Target spectrum object -> object
  :param minimalDiff:  minimalDiff: threshold of difference for each peak to be considered a broadening -> float
  :param limitRange: ppm range where to find a matching peak
  :return: list of peaks who recorded a broadening event
  '''

  peakHits = []
  matches = matchPeaks(reference=ReferenceSpectrum, spectrumB=targetSpectrum, limitRange=limitRange,
                          peakListIndex=peakListIndex)
  for match in matches:
    referencePeak, targetPeak, pos = match
    if referencePeak.lineWidths and targetPeak.lineWidths is not None:
      if len(referencePeak.lineWidths) > 0 and len(targetPeak.lineWidths) > 0:
        msg, value = comparePeakArea(referencePeak.lineWidths[0], targetPeak.lineWidths[0], minimalDiff)
        if msg == INCREASED:
          peakHits.append(match)

  return peakHits