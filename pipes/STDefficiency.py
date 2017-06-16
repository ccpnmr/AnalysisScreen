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
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe, _getWidgetByAtt
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe

########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
OffResonanceSpectrumGroup = 'OffResonanceSpectrumGroup'
OnResonanceSpectrumGroup = 'OnResonanceSpectrumGroup'
SGVarNames = [OffResonanceSpectrumGroup, OnResonanceSpectrumGroup]
RefPL = 'Reference_PeakList'
MatchPeaksWithin = 'Match_Peaks_Within_(ppm)'

## defaults
DefaultMinDist = 0.01
DefaultReferencePeakList = 0

## PipeName
PipeName = 'STD Efficiency'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################

## See AnalysisScreen Lib

########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################


class STDEfficiencyGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName


  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(STDEfficiencyGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent

    row = 0
    hw._addSGpulldowns(self, row, SGVarNames)

    row += len(SGVarNames)
    peakListLabel = Label(self.pipeFrame, RefPL, grid=(row, 0))
    setattr(self, RefPL, Spinbox(self.pipeFrame, value=0, max=0, grid=(row, 1)))

    row += 1
    minimumDistanceLabel = Label(self.pipeFrame, MatchPeaksWithin, grid=(row, 0))
    setattr(self, MatchPeaksWithin, DoubleSpinbox(self.pipeFrame, value=DefaultMinDist,
                                                 step=DefaultMinDist, min=0.01, grid=(row, 1)))

    self._updateInputDataWidgets()


  def _updateInputDataWidgets(self):
    self._setSpectrumGroupPullDowns(SGVarNames)


########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################


class STDEfficiencyPipe(SpectraPipe):

  guiPipe = STDEfficiencyGuiPipe
  pipeName = PipeName

  _kwargs  =   {
                OffResonanceSpectrumGroup: 'OffResonanceSpectrumGroup.pid',
                OnResonanceSpectrumGroup:  'OnResonanceSpectrumGroup.pid',
                MatchPeaksWithin:          DefaultMinDist,
                RefPL:                     DefaultReferencePeakList,
               }


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return:
    '''

    offResonanceSpectrumGroup = self._getSpectrumGroup(self._kwargs[OffResonanceSpectrumGroup])
    onResonanceSpectrumGroup = self._getSpectrumGroup(self._kwargs[OnResonanceSpectrumGroup])

    minimumDistance = float(self._kwargs[MatchPeaksWithin])
    nPeakList = int(self._kwargs[RefPL])

    if offResonanceSpectrumGroup and onResonanceSpectrumGroup is not None:
      # TODO
      pass

    return spectra

STDEfficiencyPipe.register() # Registers the pipe in the pipeline

