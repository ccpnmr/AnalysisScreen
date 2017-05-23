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




"""
This is a proposed new baseline correction of an NMR spectrum.
The main advantage of this method compared with other algorithms is that there aren't parameters to be set or tuned
(by the user) depending on the spectrum type.

The algorithm is divided in the following steps:

1)__ Create an array containing a subset of the discrete linear cross-correlation of the y array with an array of 128 ones.

2)__ Create y1 by Subtracting the correlated array to the original y

3)__ Estimate the baseline noise thresholds (min and max) from it
     3a)__ Thresholds automatically obtained from binning the spectrum and calulating
           the mean of  min and max of bins where no signal is found

4)__ Find the baseline of y1 using the thresholds and give zero weight to the signal peaks

5)__ Create y2 by Subtracting y1 to the baseline without signals

6)__ Find zero intensity positions in y2 plus 10 neighbors and replace them in the cross correlated array

7)__ Re-Cross-correlate using the amended correlated array

8)__ Replace y by Subtracting the latest cross correlated output

9)__ Optional, remove the baseline totally to a flat line

"""



import numpy as np
from scipy import signal


def _generateBins(yValues, nBins):
  '''
  Divide the yvalues(type=List) in nbins of equal lenghts
  Return list of lists
  '''
  bins = []
  n,b = len(yValues), 0
  yValues = list(yValues)
  for k in range(nBins):
      a, b = b, b + (n+k) // nBins
      bins.append(yValues[a:b])
  return bins


def _calculateNoiseThresholds(y, ratio=2):
  '''
  calculate the average maximum and minimum of first 10 bins.
  This is based on the assumption that there is no signal in this regions.
  TDB: make sure that this is always true.
  return: minThreshold maxThreshold as two array of same lenght of y
  '''
  maxs = []
  mins = []

  bins = _generateBins(y, 100)
  for i in bins:
    maxs.append(max(i))
    mins.append(min(i))
  if ratio == 0:
    ratio = 0.0001
  minThreshold = [np.mean(mins[0:10]) * ratio] * len(y)
  maxThreshold = [np.mean(maxs[0:10]) * ratio] * len(y)
  return minThreshold , maxThreshold


def __findIntensitiesToSetZero(x, correlatedSignal1, pos_forNonZerosY2):
  '''
  Crucial: add 10 neighbors to the found intensities. This will preserve the real peak shape
  :param x: array of x values
  :param correlatedSignal1: the correlated array obtained from y and 128 ones
  :param pos_forNonZerosY2:  list of positions where y2 should be zero
  :return: list of intensities To Set Zero
  '''
  intensitiesToSet0 = []  # heights of correlatedSignal1 where it should be 0
  for i, (pos, h) in enumerate(zip(x, correlatedSignal1)):
    for nonZeroPos in pos_forNonZerosY2:
      if nonZeroPos == pos:
        intensitiesToSet0.append(correlatedSignal1[i])
        try:
          for j in range(10):  # take also the next and previous 10 points
            intensitiesToSet0.append(correlatedSignal1[i + j])
            intensitiesToSet0.append(correlatedSignal1[i - j])
        except:
          print(ValueError)
  return intensitiesToSet0


def __find_non0_Intensity_Positions(x, y):
  '''find the positions where y is different from zero, return list of positions'''
  zeroIntensityPositions = []
  for position in np.argwhere(y != 0):
    zeroIntensityPositions.append(float(x[position]))
  return zeroIntensityPositions

def __weightPeaksOnCorrelatedSignalToZero(x, correlatedSignal1, nonZeroIntensityPositions):
  for i in __findIntensitiesToSetZero(x, correlatedSignal1, nonZeroIntensityPositions):
     correlatedSignal1[correlatedSignal1 == i] = 0

def flattenBaseline(x, y, minThreshold, maxThreshold):

  mymask = (y < minThreshold) | (y > maxThreshold)
  removeBaseline = np.ma.masked_where(mymask, y)
  removeBaseline = np.ma.filled(removeBaseline, fill_value=0)
  return x, y - removeBaseline

def baselineCorrection(x,y, flatten=False, ratio=2):

  correlatedSignal1 = signal.correlate(y, np.ones(128), mode='same')/128
  y1 = y - correlatedSignal1
  minThreshold, maxThreshold = _calculateNoiseThresholds(y1, ratio)
  baselineOnly = np.ma.filled(np.ma.masked_where((y1 < minThreshold)|(y1 > maxThreshold), y1),fill_value=0)
  nonZeroIntensityPositions = __find_non0_Intensity_Positions(x, y1 - baselineOnly)
  __weightPeaksOnCorrelatedSignalToZero(x, correlatedSignal1, nonZeroIntensityPositions)
  yC = y - signal.correlate(correlatedSignal1, np.ones(128), mode='same')/128
  if flatten:
    return flattenBaseline(x, yC, minThreshold, maxThreshold)
  else:
    return x, yC