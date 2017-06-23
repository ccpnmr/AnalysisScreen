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
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

TARGETPEAKLIST = 'Target PeakList'
REFERENCEPEAKLIST = 'Reference PeakList'


def _getReferencesFromSample(spectrum):
  '''
  Gets the reference spectra from samples.
  Sample.spectra  -> spectrum recorded using different experiment type
  Sample.sampleComponent -> substance -> referenceSpectra -> reference for the Sample.spectra exp type
  '''
  sample = spectrum.sample
  referenceSpectra = []
  if sample is not None:
    for sampleComponent in sample.sampleComponents:
      if sampleComponent is not None:
        substance = sampleComponent.substance
        if substance is not None:
          referenceSpectra += substance.referenceSpectra
  return list(set((referenceSpectra)))


def _addNewHit(spectrum, hits):
  """

  :param spectrum: CCPN spectrum object. It must have an experimentType like STD.H
  :param hits: List of tuples containing peaks hits in the form [(referencePeak, targetPeak, MatchedPosition)]
  :return:
  """
  project = spectrum.project

  spectrumHit = spectrum.newSpectrumHit(substanceName=spectrum.name)


  newTargetPeakList = spectrum.newPeakList(title=TARGETPEAKLIST, isSimulated=True, comment='PeakList containing peak hits')

  # newReferencePeakList = spectrum.newPeakList(title=REFERENCEPEAKLIST, isSimulated=True,
  #                                          comment='PeakList containing matched peak to the reference')

  referenceSpectra = []
  for  hit in hits:
    print(hit)
    if len(hit) == 3:
      referencePeak, targetPeak, position = hit
      referenceSpectra.append(referencePeak.peakList.spectrum)
      newPeakFromTarget = targetPeak.copyTo(newTargetPeakList)

      newPeakFromTarget.annotation = referencePeak.pid #hack but we need to link the reference Peak to the target Peak.
      referencePeak.annotation = newPeakFromTarget.pid #hack but we need to link the reference Peak to the target Peak.

      newPeakFromTarget._linkedPeak = referencePeak  # hack but we need to link the reference Peak to the target Peak.
      referencePeak._linkedPeak = newPeakFromTarget

      # newPeakFromReference = referencePeak.copyTo(newReferencePeakList)
      # newPeakFromReference.comment = 'Hit: Peak matched and copied From Reference PeakList'
      newPeakFromTarget.comment = 'Hit: Peak matched and copied From Target PeakList '

