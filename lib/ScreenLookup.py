# from ccpnmodel.ccpncore.lib.Io import Formats as ioFormats
# import os
# import csv
# from collections import OrderedDict
# import pathlib
# import pandas as pd
# from ccpn.util.Logging import getLogger , _debug3
# ######################### Excel Headers ##################
# """The excel headers for sample, sampleComponents, substances properties are named as the appear on the wrapper.
# Changing these will fail to set the attribute"""
#
# # '''REFERENCES PAGE'''
# GROUP_NAME = 'groupName'
# EXP_TYPE = 'expType'
# SPECTRUM_NAME = 'spectrumName'
# ### Substance properties: # do not change these names
# comment  = 'comment'
# smiles = 'smiles'
# synonyms = 'synonyms'
# stereoInfo = 'stereoInfo'
# molecularMass = 'molecularMass'
# empiricalFormula = 'empiricalFormula'
# atomCount = 'atomCount'
# hBondAcceptorCount = 'hBondAcceptorCount'
# hBondDonorCount = 'hBondDonorCount'
# bondCount = 'bondCount'
# ringCount = 'ringCount'
# polarSurfaceArea = 'polarSurfaceArea'
# logPartitionCoefficient = 'logPartitionCoefficient'
# userCode = 'userCode'
# sequenceString = 'sequenceString'
# casNumber = 'casNumber'
#
# # '''SAMPLES PAGE'''
# SAMPLE_NAME = 'sampleName'
# SPECTRUM_1H = 'spectrum_1H'
# SPECTRUM_OFF_RESONANCE = 'spectrum_Off_Res'
# SPECTRUM_ON_RESONANCE = 'spectrum_On_Res'
# SPECTRUM_STD = 'spectrumName_STD'
# SPECTRUM_WLOGSY = 'spectrum_WLogsy'
# ### other sample properties # do not change these names
# SAMPLE_COMPONENTS = 'referenceComponents'
# pH = 'pH'
# ionicStrength = 'ionicStrength'
# amount = 'amount'
# amountUnit = 'amountUnit'
# isHazardous = 'isHazardous'
# creationDate = 'creationDate'
# batchIdentifier = 'batchIdentifier'
# plateIdentifier = 'plateIdentifier'
# rowNumber = 'rowNumber'
# columnNumber = 'columnNumber'
#
# SpectrumType = 'spectrumType'
# BRUKER = 'Bruker'
# HDF5 = 'HDF5'
#
#
# SAMPLE_PROPERTIES =  [comment, pH, ionicStrength,  amount , amountUnit,isHazardous,creationDate, batchIdentifier,
#                       plateIdentifier,rowNumber,columnNumber]
#
# SUBSTANCE_PROPERTIES =  [comment,smiles,synonyms,stereoInfo,molecularMass,empiricalFormula,atomCount,
#                          hBondAcceptorCount,hBondDonorCount,bondCount,ringCount,polarSurfaceArea,
#                          logPartitionCoefficient,userCode,]
#
# EXP_TYPES = OrderedDict([(SPECTRUM_1H, 'H'), (SPECTRUM_OFF_RESONANCE ,'STD.H'),
#                         (SPECTRUM_ON_RESONANCE ,'STD.H'), (SPECTRUM_STD ,'STD.H'),
#                         (SPECTRUM_WLOGSY,'Water-LOGSY.H'),])
#
#
# def _loadScreenLookupFile(project, path:str, subType:str):
#   if subType == ioFormats.CSV:
#     print('Not implemented yet')
#
#   elif subType == ioFormats.EXCEL:
#     ScreenExcelReader(project, path)
#
#
# class ScreenExcelReader(object):
#   def __init__(self, project, path):
#     self._project = project
#     self._path = path
#     self._pandasFile = pd.ExcelFile(self._path)
#
#     self._createDataFrames()
#     self._createSpectrumGroups()
#
#
#     self.directoryPath = self._getWorkingDirectoryPath()
#     try:
#       self.preferences = self._project._mainWidow.application.preferences
#       self.preferences.general.dataPath = str(self.directoryPath)
#     except:
#       _debug3(getLogger(),'Data Path not set in preferences')
#
#     self.brukerDirs = self._getBrukerTopDirs()
#     if self.referencesDataFrame[SpectrumType].all() == BRUKER:
#       self.fullFilePaths = self._getFullBrukerFilePaths()
#       self.spectrumFormat = BRUKER
#     if self.referencesDataFrame[SpectrumType].all() == HDF5:
#       self.fullFilePaths = self._getFullHDF5FilePaths()
#       self.spectrumFormat = HDF5
#
#     self._loadReferenceSpectrumToProject()
#     self._createReferencesDataDicts()
#     self._initialiseParsingSamples()
#
#
#   def _createDataFrames(self):
#     self.referencesDataFrame = self._pandasFile.parse('References')
#     self.referencesDataFrame.fillna('Empty', inplace=True)
#     self.samplesDataFrame = self._pandasFile.parse('Samples')
#     self.samplesDataFrame.fillna('Empty', inplace=True)
#
#   def _getWorkingDirectoryPath(self):
#     xlsLookupPath = pathlib.Path(self._path)
#     return str(xlsLookupPath.parent)
#
#   def _getBrukerTopDirs(self):
#     dirs = os.listdir(str(self.directoryPath))
#     excludedFiles = ('.DS_Store', '.xls')
#     brukerDirs = [dir for dir in dirs if not dir.endswith(excludedFiles)]
#     return brukerDirs
#
#   def _getFullHDF5FilePaths(self):
#     paths = []
#     for spectrumName in self.referencesDataFrame[SPECTRUM_NAME]:
#       path = self.directoryPath + '/' + str(spectrumName)+'.hdf5'
#       paths.append(str(path))
#     return paths
#
#   def _getFullBrukerFilePaths(self):
#     fullPaths = []
#     for spectrumName in self.brukerDirs:
#       path = self.directoryPath + '/' + spectrumName
#       for dirname, dirnames, filenames in os.walk(path):
#         for filename in filenames:
#           if filename == '1r':
#             fullPath = os.path.join(dirname, filename)
#             fullPaths.append(fullPath)
#     return fullPaths
#
#   def _loadReferenceSpectrumToProject(self):
#
#     for spectrumName in self.referencesDataFrame[SPECTRUM_NAME]:
#       for path in self.fullFilePaths:
#         for item in path.split('/'):
#           if str(item).endswith('.hdf5'):
#             item = item.split('.')[0]
#           if item == spectrumName:
#             data = self._project.loadData(path)
#             if data is not None:
#               if len(data)>0:
#                 spectrum = data[0]
#
#
#   def _createReferencesDataDicts(self):
#     spectrum = None
#     for data in self.referencesDataFrame.to_dict(orient="index").values():
#       for key, value in data.items():
#         if key == SPECTRUM_NAME:
#           if self.spectrumFormat == BRUKER:
#             spectrum = self._project.getByPid('SP:'+str(value)+'-1')
#           else:
#             spectrum = self._project.getByPid('SP:'+str(value))
#           if spectrum is not None:
#             dataDict = {spectrum: data}
#             self._dispatchSpectrumToProjectGroups(dataDict)
#             self._createNewSubstance(dataDict)
#
#
#   def _initialiseParsingSamples(self):
#     self._createSamplesDataDicts()
#     for samplesDataDict in self.samplesDataDicts:
#       self._getSampleSpectra(samplesDataDict)
#
#
#   def _createSamplesDataDicts(self):
#     self.samplesDataDicts = []
#     for data in self.samplesDataFrame.to_dict(orient="index").values():
#       for key, value in data.items():
#         if key == SAMPLE_NAME:
#           sample = self._project.newSample(str(value))
#           dataDict = {sample: data}
#           self._setWrapperProperties(sample, SAMPLE_PROPERTIES, data)
#           self._addSampleComponents(sample, data)
#           self.samplesDataDicts.append(dataDict)
#
#   def _addSampleComponents(self, sample, data):
#     sampleComponents = [[header, sampleComponentName] for header, sampleComponentName in data.items() if
#                         header == SAMPLE_COMPONENTS]
#     for name in sampleComponents[0][1].split(','):
#       sampleComponent = sample.newSampleComponent(name=(str(name) + '-1'))
#       sampleComponent.role = 'Compound'
#
#
#   def _getSampleSpectra(self, samplesDataDict):
#     for sample, data in samplesDataDict.items():
#       for spectrumNameHeader, experimentType in EXP_TYPES.items():
#         spectrum = self._getSpectrum(data, spectrumNameHeader)
#         if spectrum:
#           if spectrumNameHeader == SPECTRUM_OFF_RESONANCE:
#             spectrum.comment = SPECTRUM_OFF_RESONANCE
#           if spectrumNameHeader == SPECTRUM_ON_RESONANCE:
#             spectrum.comment = SPECTRUM_ON_RESONANCE
#           spectrum.experimentType = experimentType
#           sample.spectra += (spectrum, )
#
#
#   def _getSpectrum(self, data, header):
#       spectrumName = [[excelHeader, value] for excelHeader, value in data.items()
#                                   if excelHeader == header and value != 'Empty']
#       if len(spectrumName)>0:
#         brukerDir = [str(spectrumName[0][1])]
#         path = self._getFullBrukerFilePaths()
#         spectrum = self._project.loadData(path[0])
#         return spectrum[0]
#
#   def _createSpectrumGroups(self):
#     from collections import Counter
#     counteredGroups = Counter(self.referencesDataFrame[GROUP_NAME])
#     sortedGroups = [[k, ] * v for k, v in counteredGroups.items()]
#     filteredGroups = [i for j in sortedGroups for i in list(set(j))]
#     for groupName in filteredGroups:
#       name = self._checkDuplicatedSpectrumGroupName(groupName)
#       newSG =  self._createNewSpectrumGroup(name)
#
#   def _checkDuplicatedSpectrumGroupName(self, name):
#     for sg in self._project.spectrumGroups:
#       if sg.name == name:
#         name += '@'
#     return name
#
#   def _createNewSpectrumGroup(self, name):
#     if not self._project.getByPid('SG:' + name):
#       return self._project.newSpectrumGroup(name=str(name))
#     else:
#       name = self._checkDuplicatedSpectrumGroupName(name)
#       self._createNewSpectrumGroup(name)
#
#   def _addSpectrumToSpectrumGroup(self, spectrumGroup, spectrum):
#     spectrumGroup.spectra += (spectrum,)
#
#   def _dispatchSpectrumToProjectGroups(self, dataDict):
#     for spectrum, data in dataDict.items():
#       spectrumGroupName = data[GROUP_NAME]
#       spectrumGroup = self._project.getByPid('SG:'+spectrumGroupName)
#       if spectrumGroup is not None:
#         self._addSpectrumToSpectrumGroup(spectrumGroup, spectrum)
#
#   def _createNewSubstance(self, dataDict):
#     for spectrum, data in dataDict.items():
#       substance = self._project.newSubstance(name=spectrum.id)
#       substance.referenceSpectra = [spectrum]
#       self._setWrapperProperties(substance, SUBSTANCE_PROPERTIES, data)
#
#   def _setWrapperProperties(self, wrapperObject, properties, dataframe):
#     for property in properties:
#       if property == 'synonyms':
#         setattr(wrapperObject, property, (self._getDFValue(property, dataframe),))
#       else:
#         try:
#           setattr(wrapperObject, property, self._getDFValue(property, dataframe))
#         except Exception as e:
#           _debug3(getLogger(), msg=(e, property))
#
#
#   def _getDFValue(self, header, data):
#     value = [[excelHeader, value] for excelHeader, value in data.items()
#                      if excelHeader == str(header) and value != 'Empty']
#     if len(value) > 0:
#       return value[0][1]