
import numpy as np
import pandas as pd
import glob
import os
from collections import namedtuple

filePathsProtein = glob.glob("/Users/luca/Desktop/PlainDataKen/Protein/*.tsv")
filePathsReference = glob.glob("/Users/luca/Desktop/PlainDataKen/Reference/*.tsv")


ExpType = {
          'H':'water',
          'H[t1rho(H)]': 't1',
          'Water-LOGSY.H':'wlogsy',
          'STD.H':'satxfer',
          }



def _getDataFrame(fileName):
  dataFrame = pd.read_table(fileName)
  dataFrame.columns = ['x', 'y']
  # dataFrame = dataFrame.drop('n', 1)
  return dataFrame



def __getExpType(fileName):
  for n, e in ExpType.items():
    filename = fileName.split('_')
    if str(e) in filename:
      return n


def __getSpectra(filePaths=None):
  filePaths = ['/Users/luca/PycharmProjects/LucaCodes/screening1/data/real_data/10.csv',
              '/Users/luca/PycharmProjects/LucaCodes/screening1/data/real_data/10s.csv',
              '/Users/luca/PycharmProjects/LucaCodes/screening1/data/real_data/10ss.csv']
  spectra = []
  for path in filePaths:
    fileName = path.split('/')[-1].split('.')[0]
    print(fileName)
    # try:
    #   pid = fileName.split('-')[1]
    # except:
    #   pid = fileName.split('-')[0]
    dataFrame = _getDataFrame(path)
    x = dataFrame.as_matrix(columns=['x']).ravel()
    y = dataFrame.as_matrix(columns=['y']).ravel()
    expType = '1H' #__getExpType(fileName)
    spectrum  = (fileName, x, y, expType)
    spectra.append(spectrum)
  return spectra

# Spectra_Protein = __getSpectra(filePathsProtein)
# Spectra_Reference = __getSpectra(filePathsReference)


def _createDummies(spectra, suffix=None):
  for sp in spectra:
    fileName, x, y, expType = sp
    ds = project.createDummySpectrum(('H',), str(suffix)+fileName)
    ds._positions = x
    ds._intensities = y
    # ds.experimentType = expType


spectra = __getSpectra()

_createDummies(spectra,)
# _createDummies(Spectra_Reference, suffix='Ref-')

#  all in
import pandas as pd
filePaths = ['/Users/luca/PycharmProjects/LucaCodes/screening1/data/demoDataset1/component_1_WL_No_Target.csv',
             '/Users/luca/PycharmProjects/LucaCodes/screening1/data/demoDataset1/component_2_WL_No_Target.csv',
             '/Users/luca/PycharmProjects/LucaCodes/screening1/data/demoDataset1/component_3_WL_No_Target.csv',
             '/Users/luca/PycharmProjects/LucaCodes/screening1/data/demoDataset1/component_1_WL_Yes_Target.csv',
             '/Users/luca/PycharmProjects/LucaCodes/screening1/data/demoDataset1/component_2_WL_Yes_Target.csv',
             '/Users/luca/PycharmProjects/LucaCodes/screening1/data/demoDataset1/component_3_WL_Yes_Target.csv']
spectra = []
for path in filePaths:
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
a = project.spectra[0]
b = project.spectra[1]
c = project.spectra[2]
d = project.spectra[3]
f = project.spectra[4]
g = project.spectra[5]

path = '/Users/luca/AnalysisV3/data/testProjects/AnalysisScreen_Demo1/demoWaterLogsy/'
a_fullPath = str(path)+str(a.name)+'.hdf5'
b_fullPath = str(path)+str(b.name)+'.hdf5'
c_fullPath = str(path)+str(c.name)+'.hdf5'
d_fullPath = str(path)+str(d.name)+'.hdf5'
f_fullPath = str(path)+str(f.name)+'.hdf5'
g_fullPath = str(path)+str(g.name)+'.hdf5'

convertDataToHdf5(a, a_fullPath)
convertDataToHdf5(b, b_fullPath)
convertDataToHdf5(c, c_fullPath)
convertDataToHdf5(d, d_fullPath)
convertDataToHdf5(f, f_fullPath)
convertDataToHdf5(g, g_fullPath)