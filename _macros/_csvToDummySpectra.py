
############## ========= PRIVATE ========= #########################


#  all in
import  glob
import pandas as pd
output_path='/Users/luca/Desktop/demoDatasetHDF5/'
input_paths = glob.glob("/Users/luca/Desktop/demoDataset/*.csv")


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
