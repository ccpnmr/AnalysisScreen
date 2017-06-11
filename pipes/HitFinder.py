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
    self.referenceSpectrumLabel = Label(self.pipeFrame, 'Reference Spectrum Group',  grid=(0,0))
    setattr(self, ReferenceSpectrumGroup, PulldownList(self.pipeFrame, grid=(0, 1)))

    self.targetSpectrumLabel = Label(self.pipeFrame, 'Target Spectrum Group', grid=(1, 0))
    setattr(self, TargetSpectrumGroup, PulldownList(self.pipeFrame, grid=(1, 1)))

    self.minimumDistanceLabel = Label(self.pipeFrame, text='Minimum Distance between two peaks (ppm)',  grid=(2, 0))
    setattr(self, MinimumDistance, LineEdit(self.pipeFrame, text=str(0.001),  grid=(2, 1), hAlign='l'))

    self._updateWidgets()

  def _updateWidgets(self):
    self._setDataPullDowns()


  def _setDataPullDowns(self):
    data = list(self.spectrumGroups)
    if len(data)>0:
      spectrumGroups = []
      for datum in data:
        if isinstance(datum, SpectrumGroup):
          spectrumGroups.append(datum)
      if len(spectrumGroups)>0:
        _getWidgetByAtt(self, ReferenceSpectrumGroup).setData(texts=[sg.pid for sg in spectrumGroups], objects=spectrumGroups)
        _getWidgetByAtt(self, TargetSpectrumGroup).setData(texts=[sg.pid for sg in spectrumGroups], objects=spectrumGroups)

        # Hack to select reference spectrum group in the correct box by matching name
        for sg in spectrumGroups:
          if ReferenceSpectrumGroupName == sg.name:
            _getWidgetByAtt(self, ReferenceSpectrumGroup).select(sg)









########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class HitFinder(SpectraPipe):

  guiPipe = HitFinderGuiPipe
  pipeName = PipeName

  _kwargs  =   {
               ReferenceSpectrumGroup: 'spectrumGroup.pid',
               TargetSpectrumGroup: 'spectrumGroup.pid',
               }



  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: aligned spectra
    '''
    print('Not Implemented')



HitFinder.register() # Registers the pipe in the pipeline


