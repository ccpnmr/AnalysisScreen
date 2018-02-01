
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
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 17, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


#  all in
import  glob
import numpy as np
import pandas as pd

def initMacro(project, directoryPath, type='csv'):
  """directoryPath: top directory containing all the csv files.
  Format like /Users/me/Desktop/
  """
  ## parse CSV
  input_paths = glob.glob(directoryPath+"*."+type)
  for path in input_paths:
    fileName = path.split('/')[-1].split('.')[0]
    dataFrame = pd.read_table(path)
    print(path, dataFrame)
    dataFrame.columns = ['x', 'y']
    positions = dataFrame.as_matrix(columns=['x']).ravel()
    intensities = dataFrame.as_matrix(columns=['y']).ravel()

    ## create spectrum
    spectrum = project.createDummySpectrum(('H',), str(fileName))
    spectrum.positions = positions
    spectrum.intensities = intensities
    spectrum.referencePoints = (0.0,)
    spectrum.referenceValues = (spectrum.positions[0],)
    spectrum.pointCounts = (len(spectrum._intensities),)
    spectrum.spectralWidths = ((spectrum.positions[0] + abs(spectrum.positions[-1])),)

  ## create dataset to store the positions and intensities.
  dataSet = project.newDataSet(title='spectra')
  for spectrum in project.spectra:
    data = dataSet.newData(name=spectrum.pid)
    data.attachedObjectPid = spectrum.pid
    data.attachedObject = spectrum
    data.setParameter('positions',spectrum.positions)
    data.setParameter('intensities',spectrum.intensities)

initMacro(project, '/Users/luca/Desktop/phd/data/Andrea_Beatson/txt/', type='txt')