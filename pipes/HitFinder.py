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
from ccpn.AnalysisScreen.lib.experimentAnalysis.LineBroadening import findBroadenedPeaks
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
ReferencePeakList = 'referencePeakList'
SearchModeOptions = {'LineBroadening':findBroadenedPeaks, 'IntesityChanged': None}
MinimumEfficiency = 'minimalEfficiency'

DefaultEfficiency = 10
ReferenceSpectrumGroupName = 'References'
DefaultReferencePeakList =  0

PipeName = 'LW Broadening Hit Finder'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################






########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################




class LWHitFinderGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName


  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(LWHitFinderGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent
    row = 0
    self.referenceSpectrumLabel = Label(self.pipeFrame, 'Reference Spectrum Group',  grid=(row,0))
    setattr(self, ReferenceSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.targetSpectrumLabel = Label(self.pipeFrame, 'Target Spectrum Group', grid=(row, 0))
    setattr(self, TargetSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.peakListLabel = Label(self.pipeFrame, 'Reference PeakList', grid=(row, 0))
    setattr(self, ReferencePeakList, PulldownList(self.pipeFrame, texts=[str(n) for n in range(5)], grid=(row, 1)))


    row += 1
    self.mLabel = Label(self.pipeFrame, 'Minimal Default Efficiency' , grid=(row, 0))
    setattr(self, MinimumEfficiency, DoubleSpinbox(self.pipeFrame, value=DefaultEfficiency, grid=(row, 1), hAlign='l'))

    row += 1
    self.minimumDistanceLabel = Label(self.pipeFrame, text='Match peaks within (ppm)',  grid=(row, 0))
    setattr(self, MinimumDistance, DoubleSpinbox(self.pipeFrame, value=DefaultMinimumDistance,
                                                 step=DefaultMinimumDistance, min=0.01, grid=(row, 1), hAlign='l'))

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




class LWHitFinder(SpectraPipe):

  guiPipe = LWHitFinderGuiPipe
  pipeName = PipeName

  _kwargs  =   {
               ReferenceSpectrumGroup: 'spectrumGroup.pid',
               TargetSpectrumGroup:    'spectrumGroup.pid',
               SearchMode:              list(SearchModeOptions.keys())[0],
               MinimumDistance:         DefaultMinimumDistance,
               MinimumEfficiency:       DefaultEfficiency,
               ReferencePeakList:       DefaultReferencePeakList,
               }

  def _addNewHit(self, spectrum, hits):
    spectrum.newSpectrumHit(substanceName = spectrum.name)
    npl = spectrum.newPeakList(title = 'Hits', isSimulated=True, comment='PeakList containing peak hits')
    for hit in hits:
      if hit is not None:
        referencePeak , targetPeak, position = hit
        referencePeak.copyTo(npl)
        referencePeak.annotation = 'hit'
        targetPeak.annotation = 'hit'


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: aligned spectra
    '''

    referenceSpectrumGroup = self._getSpectrumGroup(self._kwargs[ReferenceSpectrumGroup])
    targetSpectrumGroup = self._getSpectrumGroup(self._kwargs[TargetSpectrumGroup])
    searchMode = self._kwargs[SearchMode]
    minimumDistance = float(self._kwargs[MinimumDistance])
    minimumEfficiency = float(self._kwargs[MinimumEfficiency])
    nPeakList = int(self._kwargs[ReferencePeakList])

    if referenceSpectrumGroup and targetSpectrumGroup is not None:
      if len(referenceSpectrumGroup.spectra) == len(targetSpectrumGroup.spectra):
        for referenceSpectrum, targetSpectrum in zip(referenceSpectrumGroup.spectra, targetSpectrumGroup.spectra):
            print('Start')
            hits = findBroadenedPeaks(referenceSpectrum, targetSpectrum, minimalDiff=0.05, limitRange=minimumDistance,
                                      peakListIndex=nPeakList)

            if len(hits)>0:
              print(referenceSpectrum, hits)
              self._addNewHit(referenceSpectrum, hits)



    return spectra

LWHitFinder.register() # Registers the pipe in the pipeline


