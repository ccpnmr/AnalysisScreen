
############## ========= PRIVATE  MACRO ========= #########################


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
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 17, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

'''
opens a csv file containing two columns x,y values
converts to ccpn spectra
save as hdf5 in disk

Give input path and where to save the files

'''


#  all in
import  glob
import pandas as pd
output_path='/Users/luca/PycharmProjects/LucaCodes/screening1/data/real_data/hdf5/'
input_paths = glob.glob("/Users/luca/PycharmProjects/LucaCodes/screening1/data/real_data/*.csv")


for path in input_paths:
  fileName = path.split('/')[-1].split('.')[0]
  dataFrame = pd.read_csv(path)
  dataFrame.columns = ['','x', 'y']
  x = dataFrame.as_matrix(columns=['x']).ravel()
  y = dataFrame.as_matrix(columns=['y']).ravel()
  ds = project.createDummySpectrum(('H',), str(fileName))
  ds._positions = x
  ds._intensities = y
  ds.pointCounts = (len(y),)

from ccpn.util.Hdf5 import convertDataToHdf5

for spectrum in  project.spectra:
  spectrumPath = str(output_path)+str(spectrum.name)+'.hdf5'
  convertDataToHdf5(spectrum, spectrumPath)

ds = project.createDummySpectrum(('H',), str("TEST"))
ds.positions = [0,1,2,3,4,5]
ds.intensities = [0,0,22,0,0,0]
ds.pointCounts = (len(ds._intensities),)
ds.referenceValues = (ds.positions[0],)
ds.totalPointCounts = (len(ds._intensities),)
ds.aliasingLimits = ((0,5),)
print(ds.aliasingLimits, ds.spectrumLimits)
from ccpn.util.Hdf5 import convertDataToHdf5
convertDataToHdf5(ds, "/Users/luca/Desktop/test.hdf5")

# Using just python
import numpy as np
f = open("/Users/luca/Desktop/cpd_WL.csv", "r")
lines = f.read().split("\n") # "\r\n" if needed
x = []
y = []
for line in lines:
    if line != "": # add other needed checks to skip titles
        cols = line.split(",")
        x.append(float(cols[0]))
        y.append(float(cols[1]))
xArray = np.array(x)
yArray = np.array(y)

ds = project.createDummySpectrum(('H',), str("TEST"))
ds.positions = np.around(xArray,3)
ds.intensities = yArray
ds.referencePoints = (0.0,)
ds.referenceValues = (ds.positions[0],)
ds.pointCounts = (len(ds._intensities),)
ds.spectralWidths = ((ds.positions[0] + abs(ds.positions[-1])),)
from ccpn.util.Hdf5 import convertDataToHdf5
convertDataToHdf5(ds, outputPath="/Users/luca/Desktop/cpd_WL.hdf5" )
