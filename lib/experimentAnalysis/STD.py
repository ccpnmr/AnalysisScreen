#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:25 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================



import numpy as np
from ccpn.AnalysisScreen.lib.experimentAnalysis.MatchPositions import matchPeaks
import decimal

def spectrumDifference(spectrumA, spectrumB):
  '''
  :param spectrumA: first spectrum
  :param spectrumB: second spectrum
  :return: diff. An array  with the abs intensity
          difference between the two spectra
          Spectrum A and B must have the same number of position points.

          This array can be used for create a new spectrum. Like an STD
  '''
  if hasattr(spectrumA, 'intensities'):
    if hasattr(spectrumB, 'intensities'):
      diff = abs(spectrumA.intensities - spectrumB.intensities)
      return diff
    else:
      return np.array([])
  else:
    return np.array([])

def _find_STD_Hits(stdSpectrum, referenceSpectra:list, refPeakListIndex=0,limitRange=0.01, minEfficiency=0.005):
  hits = []
  useFilteredHits = False
  if referenceSpectra:
    for referenceSpectrum in referenceSpectra:
      matches = matchPeaks(reference=referenceSpectrum, spectrumB=stdSpectrum, limitRange=limitRange,
                           refPeakListIndex=refPeakListIndex)
      filteredMatches = []
      for match in matches:
        referencePeak, targetPeak, pos = match
        if targetPeak.figureOfMerit != 1.0: #default value
          useFilteredHits = True
          if targetPeak.figureOfMerit >= minEfficiency:
            filteredMatches.append(match)
      if useFilteredHits:
        hits.append(filteredMatches)
      else:
        hits.append(matches)
  else:
    print('Reference Spectra Not Given')
  return hits

def _findFalsePositiveHits(targetHits, controlHits, limitRange=0.01):

  '''
  :param targetHits: list of peaks considered hit on the target spectrum 
  :param controlHits: list of peaks considered hit on the control spectrum 
  :param limitRange: limit in ppm to match two peaks as identical
  :return: Checks hits in the control spectrum and target spectrum.
           If the same peak appears in both, then flag the target hit as false positive
  '''
  falsePositivePeaks = []
  for targetHit in targetHits:
    for controlHit in controlHits:
      if abs(targetHit.position[0] - controlHit.position[0]) <= limitRange:
        falsePositivePeaks.append(targetHit)
        targetHit.comment = 'False positive hit'
  return falsePositivePeaks



# def _find_STD_Hits(stdSpectrum, referenceSpectra: list, isMixture=False,
#                   limitRange=0.01, minEfficiency=None, maxEfficiency=None, excludeRegions=None):
#   hits = []
#   if referenceSpectra:
#     for referenceSpectrum in referenceSpectra:
#       matches = matchPeaks(reference=referenceSpectrum, spectrumB=stdSpectrum, limitRange=limitRange)
#       hits.append(matches)
#   return hits


def _calculatePeakEffiency(stdSpectrum, onResonanceSpectrum, offResonanceSpectrum, n_peakList=0, limitRange=0.01):
  ''' matchs the hit peak to the on and off Resonance and determines the efficiency change'''
  # if not onResonanceSpectrum.peakLists[n_peakList].peaks and not offResonanceSpectrum.peakLists[n_peakList].peaks: return


  matches = matchPeaks(reference=offResonanceSpectrum, spectrumB=onResonanceSpectrum, limitRange=limitRange,
                       refPeakListIndex=n_peakList)
  meritItems = []
  for match in matches:
    offpeak, onPeak, pos = match
    if float(offpeak.height) != 0.00:
      merit = (abs(offpeak.height - onPeak.height)) / offpeak.height
      pos = (offpeak.position[0]+onPeak.position[0])/2
      meritItems.append((merit, pos))

  for item in meritItems:
    if len(item)==2:
      merit, pos = item
      if len(stdSpectrum.peakLists)>n_peakList:
        for stdPeak in stdSpectrum.peakLists[n_peakList].peaks:
          if abs(stdPeak.position[0]-pos) <= limitRange:
            stdPeak.figureOfMerit = merit

#     fullValue = ((abs(referencePeak.height - targetPeak.height)) / referencePeak.height) * 100
#     value = decimal.Decimal(fullValue).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)

