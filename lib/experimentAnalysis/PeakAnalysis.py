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
__version__ = "$Revision: 3.0.b5 $"
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
    if isPositive(referenceIntensity) == isPositive(spectrumBIntensity):
        return False
    else:
        return True


def getIntensiyChange(reference, intensityB):
    '''compare the reference intensity and a target intensity
      return the difference '''

    if intensityB is not None:
        return reference - intensityB


def getPercentageIntensiyChange(intensityB, difference):
    '''compare the reference intensity and a target intensity
      return the percentage of difference. It can be used for STD efficiency '''

    try:
        percentage = difference / intensityB * 100.0
    except ZeroDivisionError:
        return 0
    return percentage
