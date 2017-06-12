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
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from scipy import signal
import numpy as np


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################

OffResonanceSpectrumGroup = 'OffResonanceSpectrumGroup'
OnResonanceSpectrumGroup = 'OnResonanceSpectrumGroup'

OnResonance = 'OnResonance'
OffResonance = 'OffResonance'

newSTDSpectrumGroupName = 'newSTDSpectrumGroupName'
DefaultSTDSGname = 'STD'

PipeName = 'STD Creator'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################






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
    self.offResonanceLabel = Label(self.pipeFrame, OffResonance+' Spectrum Group',  grid=(row,0))
    setattr(self, OffResonanceSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.targetSpectrumLabel = Label(self.pipeFrame, OnResonance+' Spectrum Group', grid=(row, 0))
    setattr(self, OnResonanceSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.newSTDSpectrumGroupLabel = Label(self.pipeFrame, 'New STD Spectrum Group Name', grid=(row, 0))
    setattr(self, newSTDSpectrumGroupName, LineEdit(self.pipeFrame, text=DefaultSTDSGname, textAligment='l', grid=(row, 1)))

    self._updateWidgets()

  def _updateWidgets(self):
    self._setDataPullDowns()


  def _setDataPullDowns(self):
    spectrumGroups = list(self.spectrumGroups)
    if len(spectrumGroups)>0:
      _getWidgetByAtt(self, OffResonanceSpectrumGroup).setData(texts=[sg.pid for sg in spectrumGroups], objects=spectrumGroups)
      _getWidgetByAtt(self, OnResonanceSpectrumGroup).setData(texts=[sg.pid for sg in spectrumGroups], objects=spectrumGroups)

      # trying to select reference spectrum group in the correct pulldown by matching name
      for sg in spectrumGroups:
        if OnResonance in sg.name:
          _getWidgetByAtt(self, OnResonanceSpectrumGroup).select(sg)
        elif OffResonance in sg.name:
          _getWidgetByAtt(self, OffResonanceSpectrumGroup).select(sg)









########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class STDCreator(SpectraPipe):

  guiPipe = STDCreatorGuiPipe
  pipeName = PipeName

  _kwargs  =   {
                OffResonanceSpectrumGroup : 'OffResonanceSpectrumGroup.pid',
                OnResonanceSpectrumGroup : 'OnResonanceSpectrumGroup.pid',
                newSTDSpectrumGroupName:   DefaultSTDSGname,
               }


  def _getSpectrumGroup(self, pid):
    return self.project.getByPid(pid)

  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: aligned spectra
    '''
    #
    # referenceSpectrumGroup = self._getSpectrumGroup(self._kwargs[ReferenceSpectrumGroup])
    # targetSpectrumGroup = self._getSpectrumGroup(self._kwargs[TargetSpectrumGroup])
    # searchMode = self._kwargs[SearchMode]
    # minimumDistance = float(self._kwargs[MinimumDistance])
    # minimumEfficiency = float(self._kwargs[MinimumEfficiency])
    # nPeakList = int(self._kwargs[ReferencePeakList])
    #
    # if referenceSpectrumGroup and targetSpectrumGroup is not None:
    #   if len(referenceSpectrumGroup.spectra) == len(targetSpectrumGroup.spectra):
    #     for referenceSpectrum, targetSpectrum in zip(referenceSpectrumGroup.spectra, targetSpectrumGroup.spectra):
    #         print('Start')
    #         hits = findBroadenedPeaks(referenceSpectrum, targetSpectrum, minimalDiff=0.05, limitRange=minimumDistance,
    #                                   peakListIndex=nPeakList)
    #
    #         if len(hits)>0:
    #           print(referenceSpectrum, hits)
    #           self._addNewHit(referenceSpectrum, hits)
    #
    #

    return spectra

STDCreator.register() # Registers the pipe in the pipeline


