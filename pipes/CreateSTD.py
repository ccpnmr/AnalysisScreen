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


#### GUI IMPORTS
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe , _getWidgetByAtt
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.AnalysisScreen.lib.experimentAnalysis.STD import spectrumDifference
from ccpn.pipes.lib._new1Dspectrum import _create1DSpectrum

########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################

OffResonanceSpectrumGroup = 'OffResonanceSpectrumGroup'
OnResonanceSpectrumGroup = 'OnResonanceSpectrumGroup'
SGVarNames = [OffResonanceSpectrumGroup, OnResonanceSpectrumGroup]

NewSTDSpectrumGroupName = 'New_STD_SpectrumGroup_Name'
DefaultSTDname = 'STD_'

PipeName = 'STD Creator'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################

def _createSTDs(project, offResonanceSpectrumGroup, onResonanceSpectrumGroup):
  spectraSTD = []
  if offResonanceSpectrumGroup and onResonanceSpectrumGroup is not None:
    if len(offResonanceSpectrumGroup.spectra) == len(onResonanceSpectrumGroup.spectra):
      for offResSpectrum, onResSpectrum in zip(offResonanceSpectrumGroup.spectra, onResonanceSpectrumGroup.spectra):
        stdIntensities = spectrumDifference(offResSpectrum, onResSpectrum)
        stdPositions = offResSpectrum.positions
        std = _create1DSpectrum(project, DefaultSTDname+offResSpectrum.name, stdIntensities, stdPositions, 'STD.H')
        spectraSTD.append(std)
  return spectraSTD

########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################


class STDCreatorGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName


  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(STDCreatorGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent

    row = 0
    hw._addSGpulldowns(self, row, SGVarNames)
    row += len(SGVarNames)

    self.newSTDSpectrumGroupLabel = Label(self.pipeFrame, NewSTDSpectrumGroupName, grid=(row, 0))
    setattr(self, NewSTDSpectrumGroupName, LineEdit(self.pipeFrame, text=DefaultSTDname, textAligment='l', hAlign='l', grid=(row, 1)))

    self._updateInputDataWidgets()

  def _updateInputDataWidgets(self):
    self._setSpectrumGroupPullDowns(SGVarNames)


########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################


class STDCreator(SpectraPipe):

  guiPipe = STDCreatorGuiPipe
  pipeName = PipeName

  _kwargs  =   {
                OffResonanceSpectrumGroup : 'OffResonanceSpectrumGroup.pid',
                OnResonanceSpectrumGroup : 'OnResonanceSpectrumGroup.pid',
                NewSTDSpectrumGroupName:   DefaultSTDname,
               }





  def _createNewSTDspectrumGroup(self, name, stdSpectra):
    newSTDspectrumGroup = None
    if not self.project.getByPid('SG:'+name):
      newSTDspectrumGroup = self.project.newSpectrumGroup(name = name, spectra = stdSpectra)
    else:
      newSTDspectrumGroup = self.project.newSpectrumGroup(name=name+'_new', spectra=stdSpectra)

    if newSTDspectrumGroup is not None:
      return newSTDspectrumGroup

  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: aligned spectra
    '''

    offResonanceSpectrumGroup = self._getSpectrumGroup(self._kwargs[OffResonanceSpectrumGroup])
    onResonanceSpectrumGroup = self._getSpectrumGroup(self._kwargs[OnResonanceSpectrumGroup])
    newSTDSpectrumGroupName = self._kwargs[NewSTDSpectrumGroupName]

    stds = _createSTDs(self.project, offResonanceSpectrumGroup, onResonanceSpectrumGroup)
    if len(stds)==len(offResonanceSpectrumGroup.spectra):
      newSTDspectrumGroup = self._createNewSTDspectrumGroup(name=newSTDSpectrumGroupName, stdSpectra= stds)
      self.spectrumGroups.update([newSTDspectrumGroup])

      listsOfSpectra =  [onResonanceSpectrumGroup.spectra, offResonanceSpectrumGroup.spectra, newSTDspectrumGroup.spectra]
      spectra = [spectrum for spectra in listsOfSpectra for spectrum in spectra]

    return set(spectra)

STDCreator.register() # Registers the pipe in the pipeline


