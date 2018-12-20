
############## ========= PRIVATE  MACRO ========= #########################


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
opens a txt file containing two columns x,y values
converts to ccpn spectra
save as hdf5 in disk

Give input path and where to save the files

'''


import  glob
import pandas as pd


output_path='/Users/luca/Desktop/Andrea_Beatson/'
input_paths = glob.glob("/Users/luca/Desktop/Andrea_Beatson/*.txt")


for path in input_paths:
  fileName = path.split('/')[-1].split('.')[0]
  dataFrame = pd.read_table(path)
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
