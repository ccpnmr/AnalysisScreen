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
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 17, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


'''

17/02/2017

To compare two spectra, whether ref vs Spectrum with target  or
Spectrum without target vs Spectrum with target.

Matching Peaks


'''

import numpy as np
import inspect

currentFile = inspect.getfile(inspect.currentframe())



def matchingPosition(data, limitMax, limitMin):
  '''

  Data: the list of peak positions.
  limitRange: the limit to add on the left and on the right

  :return: array with matching positions
  '''

  return data[np.argwhere(np.logical_and(data <= limitMax, data >= limitMin))]




def excludeFromComparing(data, excludeRegions):
  ''' excludeRegions: list of lists E.G. [['start','stop'],  '...', ['start','stop']]'''
  ll = []
  for region in excludeRegions:
    if not region:
      return data
    if region:
      start, stop = region
      ll.append(data[np.argwhere(np.logical_and(data <= start, data >= stop))])
  if ll:
    ll = np.concatenate(ll, axis = 0)
    data = [j for j in data if j not in ll]
    return np.array(data)



def matchPeaks(reference, spectrumB, limitRange, refPeakListIndex=0, ):
  '''
  spectrum object type CCPN. Assumes it has a peaklist and peaks object
  :param reference: the reference spectrum object
  :param spectrumB: the spectrum object to match against the reference
  :param limitRange: ppm range where to find a matching peak
  :return:Tuple of reference Peak, target Peak, position of match
  '''

  allMatches = []
  if len(reference.peakLists)>refPeakListIndex:
    referencePeakPositions = np.array([peak.position[0] for peak in reference.peakLists[refPeakListIndex].peaks if peak.position])
    for peakB in spectrumB.peakLists[refPeakListIndex].peaks:
      peakBpos = peakB.position[0]
      matches = matchingPosition(referencePeakPositions, peakBpos+limitRange, peakBpos-limitRange)
      referencePeaks = [peak for peak in reference.peakLists[refPeakListIndex].peaks if peak.position[0] in matches]
      if referencePeaks:
        allMatches.append((referencePeaks[0], peakB, matches))

  return allMatches


def matchHitToReference(spectrumHit, referenceSpectra, limitRange=0.01, refPeakListIndex=0):
  '''

  :param targetHitSpectrum: spectrum calculated as hit (peak linewhidths changed compared to its control)
  :param referenceSpectra: list of reference spectra. Eg mixture or single reference spectrum
  :return: matches of the hit peak to the references
  '''

  hits = []
  if referenceSpectra:
    for referenceSpectrum in referenceSpectra:
      if len(referenceSpectrum.peakLists) > refPeakListIndex:
        matches = matchPeaks(reference=referenceSpectrum, spectrumB=spectrumHit, limitRange=limitRange,
                             refPeakListIndex=refPeakListIndex)
        hits.append(matches)

  return hits
