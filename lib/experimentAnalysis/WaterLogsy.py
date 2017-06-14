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
__date__ = "$Date: 2017-02-16 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

SignChanged = 'SignChanged'
IntensityChanged = 'intensityChanged'
PositiveOnly = 'positiveOnly'
MissingPeak = 'MissingPeak'

MODES = [IntensityChanged, PositiveOnly, SignChanged]

import numpy as np
from ccpn.AnalysisScreen.lib.experimentAnalysis import MatchPositions as mp
from ccpn.AnalysisScreen.lib.experimentAnalysis import PeakAnalysis as pa



def __positiveHits(wlT_Peaks, wlT_PeakPos_filtered):
  ## if not control is given, find Only If there are positive peaks.
  hits = []
  for wlPeak in wlT_Peaks:
    if pa.intensitySignChanged(-1, wlPeak.height):
      if wlPeak.position[0] in wlT_PeakPos_filtered:
        hits.append({'wLControlPeak': None, 'TargetPeak': wlPeak,
                     'Pos': wlPeak.position[0], 'HitType': PositiveOnly})
  return hits


def __matchHitsToReferences(hits, references, limitRange):
  mixtureHits = []
  for reference in references:
    referencePeaks = reference.peakLists[0].peaks

    referencePeakpos = np.array([referencePeak.position[0] for referencePeak in referencePeaks])
    if hits:
      referencesHits = {'referenceHit': reference, 'peakHits': []}
      for hit in hits:
        hitWLPeak = hit['TargetPeak']
        hitWLPeakpos = np.array(hitWLPeak.position[0])
        matches = mp.matchingPosition(referencePeakpos, hitWLPeakpos + limitRange, hitWLPeakpos - limitRange)
        rp = [peak for peak in reference.peakLists[0].peaks if peak.position[0] in matches]
        if rp:
          if len(rp) == 1:
            referencesHits['peakHits'].append(rp[0])

      if referencesHits['peakHits']:
        mixtureHits.append(referencesHits)
  return mixtureHits


def __findHitsWithoutControl(wlT_PeakPos_filtered, wlT_Peaks, isMixture, references, limitRange):
  hits = __positiveHits(wlT_PeakPos_filtered=wlT_PeakPos_filtered, wlT_Peaks=wlT_Peaks)

  if isMixture:
    if references:
      mixtureHits = __matchHitsToReferences(hits, references, limitRange)
      return mixtureHits
    else:
      # print('Reference not given. Returned WL target hits without matching to references ')
      return hits
  else:
    # print('Control not given. Returned WL target hits based on positive peaks')
    return hits


def __findHitsByMissingTargetPeaks(wLControl, wLTarget, matchedControl, peakListControl=0, peakListTarget=0):
  hits = []
  wlCPeakCount = len([peak for peak in wLControl.peakLists[peakListControl].peaks])
  wLTPeakCount = len([peak for peak in wLTarget.peakLists[peakListTarget].peaks])
  wlC_Peaks = [wlCPeak for wlCPeak in wLControl.peakLists[peakListControl].peaks]

  if wlCPeakCount != wLTPeakCount:
    missingWLT_peaks = [p for p in wlC_Peaks if p not in matchedControl]
    print('MISSING Peaks in %s but present in %s : %s'
          % (wLTarget.name, wLControl.name, missingWLT_peaks))
    for wLControlPeak in missingWLT_peaks:
      ##add new peak to peaklists of wlTarget with same position but 0 intensity. Keep it as hit
      wLTargetnewPeak = wLTarget.peakLists[peakListTarget].newPeak(position=wLControlPeak.position, intensity=0, comment='Hit')
      wLTarget.peakLists[0].peaks.append(wLTargetnewPeak)
      hits.append({'wLControlPeak': wLControlPeak, 'TargetPeak': wLTargetnewPeak,
                   'Pos': wLTargetnewPeak.position[0], 'HitType': 'MissingPeak'})
  return hits


def __findHitsByIntensityChange(wLControlPeak, TargetPeak):
  hits = []
  intensityDifferences = pa.getIntensiyChange(wLControlPeak.height, TargetPeak.height)
  if abs(intensityDifferences) > 0.0:
    hits.append({'wLControlPeak': wLControlPeak, 'TargetPeak': TargetPeak,
                 'Pos': TargetPeak.position[0], 'HitType': IntensityChanged})

  return hits


def __findHitsByMode(matches, matchedControl, wlT_PeakPos_filtered, mode):
  hits = []
  for match in matches:
    wLControlPeak, TargetPeak, pos = match
    matchedControl.append(wLControlPeak)

    if pa.intensitySignChanged(wLControlPeak.height, TargetPeak.height):
      if TargetPeak.position[0] in wlT_PeakPos_filtered:
        if mode == SignChanged:
          hits.append({'wLControlPeak': wLControlPeak, 'TargetPeak': TargetPeak,
                       'Pos': TargetPeak.position[0], 'HitType': SignChanged})
        else:
          if mode == IntensityChanged:
            intensityDifferences = pa.getIntensiyChange(wLControlPeak.height, TargetPeak.height)
            if abs(intensityDifferences) > 0.0:
              hits.append({'wLControlPeak': wLControlPeak, 'TargetPeak': TargetPeak,
                           'Pos': TargetPeak.position[0], 'HitType': IntensityChanged})

    if mode == PositiveOnly:
      if pa.isPositive(TargetPeak.height):
        hits.append({'wLControlPeak': wLControlPeak, 'TargetPeak': TargetPeak,
                     'Pos': TargetPeak.position[0], 'HitType': 'positivePeaks'})
  return hits


def __isDifferentPeakCount(wLControl, wLTarget):
  wlCPeakCount = len([peak for peak in wLControl.peakLists[0].peaks])
  wLTPeakCount = len([peak for peak in wLTarget.peakLists[0].peaks])
  if wlCPeakCount != wLTPeakCount:
    return True
  else:
    return False


def __addMissingHits(hits, wLControl, wLTarget, matchedControl):
  missingHits = __findHitsByMissingTargetPeaks(wLControl, wLTarget, matchedControl)
  for h in missingHits:
    hits.append(h)
  return hits


def findWaterLogsyHits(wLTarget, wLControl=None, references=None, mode=IntensityChanged, isMixture=False,
                       limitRange=0.0, excludeRegions=None):
  '''
  wLTarget: obj spectrum.   wl spectrum with target
  wlControl: obj spectrum.  wl spectrum without target or displacer
  references: list of obj spectrum.  1H references. Used when Wl are mixtures of more components.

  modes:str - signChanged (detects only if there are peaks that changed sign from negative to positive in the wlControl
                          to the wlTarget. Unavailable without wLControl )

            - intensityChanged (detects the intensity changes of peaks from wlControl to wlTarget.
                              Unavailable without wLControl )

            - positiveOnly (detects only if the intensity peaks of wlTarget are positive. Used if there is no wlControl.
                       NB this can give false positive hits in case of aggregation of ligands)


  limitRange: float. used for matching peaks. PPM range left and right where to search and match a peak.
  excludeRegions: region of spectrum to exclude. Format: list of lists E.G. [['start','stop'],  '...', ['start','stop']]


  peakHit in the format {'wLControlPeak': obj, 'TargetPeak': obj,'Pos': float, 'HitType': str(one of: PositiveOnly, IntensityChanged, 'missingPeak'}

  return hits:
  if only wlTarget: return -->  list[peakHit, ...]
  if mixtures with references
                list[{'referenceHit':obj Reference, 'peakHits':list[peakHit, ...]}]



  #@@
  '''

  hits = []
  if not wLTarget:
    raise ValueError('Provide a WL spectrum')
  ## get target peak positions
  wlT_Peaks = [wlPeak for wlPeak in wLTarget.peakLists[0].peaks]
  wlT_PeakPositions = [p.position[0] for p in wlT_Peaks]

  if excludeRegions:  ## filter peak positions if excludeRegions is given
    wlT_PeakPos_filtered = mp.excludeFromComparing(np.array(wlT_PeakPositions), excludeRegions)
  else:
    wlT_PeakPos_filtered = wlT_PeakPositions

  if not wLControl:  ## if not control, find Only If there are positive peaks
    hits = __positiveHits(wlT_PeakPos_filtered=wlT_PeakPos_filtered, wlT_Peaks=wlT_Peaks)
    if isMixture:
      if references:
        mixtureHits = __matchHitsToReferences(hits, references, limitRange)
        return mixtureHits
      else:
        return hits
    else:
      return hits

  matches = mp.matchPeaks(reference=wLControl, spectrumB=wLTarget, limitRange=limitRange)
  matchedControl = []
  if matches:
    hits = __findHitsByMode(matches, matchedControl, wlT_PeakPos_filtered, mode)
  if __isDifferentPeakCount(wLControl, wLTarget):
    hits = __addMissingHits(hits, wLControl, wLTarget, matchedControl)
  if isMixture:
    if references:
      mixtureHits = __matchHitsToReferences(hits, references, limitRange)
      return mixtureHits
    else:
      print('Reference not given')
      return hits
  else:
    return hits




