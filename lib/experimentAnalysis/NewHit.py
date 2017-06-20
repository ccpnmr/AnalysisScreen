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

def _addNewHit(spectrum, hits):
  """

  :param spectrum: CCPN spectrum object. It must have an experimentType like STD.H
  :param hits: List of tuples containing peaks hits in the form [(referencePeak, targetPeak, MatchedPosition)]
  :return:
  """
  project = spectrum.project
  if not project.getByPid('SH:'+spectrum.name):
    spectrumHit = spectrum.newSpectrumHit(substanceName=spectrum.name)
  else:
    spectrumHit = spectrum.newSpectrumHit(substanceName=spectrum.name+1) #avoids Api errors

  newTargetPeakList = spectrum.newPeakList(title=TARGETPEAKLIST, isSimulated=True, comment='PeakList containing peak hits')
  newReferencePeakList = spectrum.newPeakList(title=REFERENCEPEAKLIST, isSimulated=True,
                                           comment='PeakList containing matched peak to the reference')

  referenceSpectra = []
  for  hit in hits:
    if len(hit) == 3:
      referencePeak, targetPeak, position = hit
      referenceSpectra.append(referencePeak.peakList.spectrum)
      newPeakFromReference = referencePeak.copyTo(newReferencePeakList)
      newPeakFromTarget = targetPeak.copyTo(newTargetPeakList)

      newPeakFromReference.annotation = 'Hit'
      newPeakFromTarget.annotation = 'Hit'
      newPeakFromReference.comment = 'Hit: Peak matched and copied From Reference PeakList'
      newPeakFromTarget.comment = 'Hit: Peak matched and copied From Target PeakList '

  if len(referenceSpectra)>0:
    spectrumHit._referenceSpectrum = referenceSpectra[0]
    substance = referenceSpectra[0].referenceSubstance
    if substance is not None:
      if not project.getByPid('SH:' + substance.name):
        spectrumHit.rename(substance.name)
      else:
        spectrumHit.rename(substance.name+1) #avoids Api errors
