"""Module Documentation here

"""
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
__dateModified__ = "$dateModified: 2017-04-07 11:41:14 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"

__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#====================================



import pandas as pd
from scipy import signal
from collections import namedtuple, deque
import numpy as np


def getShift(ref_x, ref_y, target_y):
  '''

  :param ref_x: X array of the reference spectra (positions)
  :param ref_y: Y array of the reference spectra (intensities)
  :param target_y: Y array of the target spectra (intensities)
  :return: the shift needed to align the two spectra.
  To align the target spectrum to its reference: add the shift to the x array.
  E.g. target_y += shift

  '''
  return (np.argmax(signal.correlate(ref_y, target_y)) - len(target_y)) * np.mean(np.diff(ref_x))




def _alignSpectra(referenceSpectrum, spectra):

  alignedSpectra = []
  for sp in spectra:
    shift = getShift(ref_x=referenceSpectrum.positions, ref_y=referenceSpectrum.intensities, target_y=sp.intensities)
    sp._positions = sp.positions
    sp._positions += shift
    alignedSpectra.append(sp)
  return alignedSpectra

