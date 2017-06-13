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





def isPositive(intensity):
  ''' Used to find positive peaks by giving the intenity as float.
  Can be used for WaterLogsy or STD
  '''
  return True if intensity >= 0.0 else False


def intensitySignChanged(referenceIntensity, spectrumBIntensity):
  '''
  compare intensity signs of a reference and a target value
  Used in Finding WaterLogsy Hits.
  ReferenceIntensity: intensity from the control Spectrum. EG. WL without target.
  spectrumBIntensity: intensity from the experimental Spectrum. EG. WL with target.
  return: True if intensity sign has changed
  '''
  if isPositive(referenceIntensity) == isPositive(spectrumBIntensity):return False
  else: return True


def getIntensiyChange(reference, intensityB):
  '''compare the reference intensity and a target intensity
    return the difference '''

  if intensityB is not None:
    return reference - intensityB

def getPercentageIntensiyChange(intensityB, difference):
    '''compare the reference intensity and a target intensity
      return the percentage of difference. It can be used for STD efficiency '''

    try:
      percentage =  difference / intensityB * 100.0
    except ZeroDivisionError:
      return 0
    return percentage