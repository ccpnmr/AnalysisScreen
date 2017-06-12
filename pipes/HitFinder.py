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
from ccpn.core.SpectrumGroup import SpectrumGroup
from scipy import signal
import numpy as np


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################

ReferenceSpectrumGroup = 'referenceSpectrumGroup'
TargetSpectrumGroup = 'targetSpectrumGroup'
MinimumDistance = 'minimumDistance'
DefaultMinimumDistance = 0.01
SearchMode = 'searchMode'
SearchModeOptions = ['LineBroadening', 'IntesityChanged']
MinimumEfficiency = 'minimalEfficiency'
DefaultEfficiency = 10
ReferenceSpectrumGroupName = 'References'
PipeName = 'Hit Finder'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################






########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################




class HitFinderGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName

  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(HitFinderGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent
    row = 0
    self.referenceSpectrumLabel = Label(self.pipeFrame, 'Reference Spectrum Group',  grid=(row,0))
    setattr(self, ReferenceSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.targetSpectrumLabel = Label(self.pipeFrame, 'Target Spectrum Group', grid=(row, 0))
    setattr(self, TargetSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.searchModeLabel = Label(self.pipeFrame, 'Search Mode', grid=(row, 0))
    setattr(self, SearchMode, PulldownList(self.pipeFrame, texts=SearchModeOptions, grid=(row, 1)))

    row += 1
    self.searchModeLabel = Label(self.pipeFrame, 'Minimal Default Efficiency' , grid=(row, 0))
    setattr(self, MinimumEfficiency, DoubleSpinbox(self.pipeFrame, value=DefaultEfficiency, grid=(row, 1), hAlign='l'))

    row += 1
    self.minimumDistanceLabel = Label(self.pipeFrame, text='Match peaks within (ppm)',  grid=(row, 0))
    setattr(self, MinimumDistance, LineEdit(self.pipeFrame, text=str(DefaultMinimumDistance), textAligment='l', grid=(row, 1), hAlign='l'))

    self._updateWidgets()

  def _updateWidgets(self):
    self._setDataPullDowns()


  def _setDataPullDowns(self):
    spectrumGroups = list(self.spectrumGroups)
    if len(spectrumGroups)>0:
      _getWidgetByAtt(self, ReferenceSpectrumGroup).setData(texts=[sg.pid for sg in spectrumGroups], objects=spectrumGroups)
      _getWidgetByAtt(self, TargetSpectrumGroup).setData(texts=[sg.pid for sg in spectrumGroups], objects=spectrumGroups)

      # trying to select reference spectrum group in the correct pulldown by matching name
      for sg in spectrumGroups:
        if ReferenceSpectrumGroupName in sg.name:
          _getWidgetByAtt(self, ReferenceSpectrumGroup).select(sg)









########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class HitFinder(SpectraPipe):

  guiPipe = HitFinderGuiPipe
  pipeName = PipeName

  _kwargs  =   {
               ReferenceSpectrumGroup: 'spectrumGroup.pid',
               TargetSpectrumGroup:    'spectrumGroup.pid',
               SearchMode:              SearchModeOptions[0],
               MinimumDistance:         DefaultMinimumDistance,
               MinimumEfficiency:       DefaultEfficiency,
               }



  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: aligned spectra
    '''
    print('Not Implemented')



HitFinder.register() # Registers the pipe in the pipeline


