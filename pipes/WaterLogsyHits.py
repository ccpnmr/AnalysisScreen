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
from ccpn.ui.gui.widgets.Icon import Icon

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.AnalysisScreen.lib.experimentAnalysis import WaterLogsy as wl
from scipy import signal
import numpy as np


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
ReferenceSpectrumGroup = 'referenceSpectrumGroup'
WLcontrolSpectrumGroup = 'wlControlSpectrumGroup'
WLtargetSpectrumGroup = 'wlTargetSpectrumGroup'

MinimumDistance = 'minimumDistance'
ReferencePeakList = 'referencePeakList'
MinimumEfficiency = 'minimalEfficiency'
CalculateEfficiency = 'calculateEfficiency'
ReferenceSpectrumGroupName = 'References'
ModeHit = 'modeHit'

# MODES = [IntensityChanged, PositiveOnly, MissingPeak]

## defaults
DefaultEfficiency = 10
DefaultReferencePeakList =  0
DefaultMinimumDistance = 0.01

PulldownSGHeaderText ='-- Select SG --'

## PipeName
PipeName = 'WaterLogsy Hits'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################






########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################




class WaterLogsyHitFinderGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName


  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(WaterLogsyHitFinderGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent


    row = 0
    self.modeLabel = Label(self.pipeFrame, 'Mode', grid=(row, 0))
    setattr(self, ModeHit, PulldownList(self.pipeFrame, texts=wl.MODES, grid=(row, 1)))
    _getWidgetByAtt(self, ModeHit).activated[str].connect(self._modeCallback)
    row += 1
    self.referenceSpectrumLabel = Label(self.pipeFrame, 'Reference Spectrum Group',  grid=(row,0))
    setattr(self, ReferenceSpectrumGroup, PulldownList(self.pipeFrame, headerText=self._pulldownSGHeaderText,
                                                       headerIcon=self._warningIcon,grid=(row, 1)))

    row += 1
    self.targetSpectrumLabel = Label(self.pipeFrame, 'WL Control Spectrum Group', grid=(row, 0))
    setattr(self, WLcontrolSpectrumGroup, PulldownList(self.pipeFrame,  headerText=self._pulldownSGHeaderText,
                                                       headerIcon=self._warningIcon, grid=(row, 1)))

    row += 1
    self.targetSpectrumLabel = Label(self.pipeFrame, 'WL Target Spectrum Group', grid=(row, 0))
    setattr(self, WLtargetSpectrumGroup, PulldownList(self.pipeFrame, headerText=self._pulldownSGHeaderText,
                                                      headerIcon=self._warningIcon,  grid=(row, 1)))

    row += 1
    self.modeLabel = Label(self.pipeFrame, 'Reference PeakList', grid=(row, 0))
    setattr(self, ReferencePeakList, PulldownList(self.pipeFrame, texts=[str(n) for n in range(5)], grid=(row, 1)))

    row += 1
    self.minimumDistanceLabel = Label(self.pipeFrame, text='Match peaks within (ppm)', grid=(row, 0))
    setattr(self, MinimumDistance, DoubleSpinbox(self.pipeFrame, value=DefaultMinimumDistance,
                                                 step = DefaultMinimumDistance, grid=(row, 1), min=0.01, hAlign='l'))

    row += 1
    self.minimalEfficiencyLabel = Label(self.pipeFrame, 'Minimal  Efficiency (%)', grid=(row, 0))
    setattr(self, MinimumEfficiency, DoubleSpinbox(self.pipeFrame, value=DefaultEfficiency, grid=(row, 1), hAlign='l'))



    self._updateInputDataWidgets()

  def _updateInputDataWidgets(self):
    self._setSpectrumGroupPullDowns(widgetVariables = [ReferenceSpectrumGroup, WLcontrolSpectrumGroup, WLtargetSpectrumGroup],
                                    headerText=self._pulldownSGHeaderText, headerIcon=self._warningIcon)




  def _modeCallback(self, selected):
    'manages the spectrumgroups pullDown'
    if selected == wl.PositiveOnly:
      _getWidgetByAtt(self, WLcontrolSpectrumGroup).setEnabled(False)
      _getWidgetByAtt(self, WLcontrolSpectrumGroup)._clear()
    elif selected == wl.IntensityChanged or selected == wl.SignChanged:
      _getWidgetByAtt(self, WLcontrolSpectrumGroup).setEnabled(True)


########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class WaterLogsyHitFinderPipe(SpectraPipe):

  guiPipe = WaterLogsyHitFinderGuiPipe
  pipeName = PipeName

  _kwargs  =   {
                ReferenceSpectrumGroup: 'spectrumGroup.pid',
                WLtargetSpectrumGroup:  'spectrumGroup.pid',
                WLcontrolSpectrumGroup: 'spectrumGroup.pid',
                MinimumDistance:         DefaultMinimumDistance,
                MinimumEfficiency:       DefaultEfficiency,
                ReferencePeakList:       DefaultReferencePeakList,
               }

  def _addNewHit(self, spectrum, hits):
    # FIXME hack TODO better
    spectrum.newSpectrumHit(substanceName = spectrum.name)
    npl = spectrum.newPeakList(title = 'Hits', isSimulated=True, comment='PeakList containing peak hits')
    for lst in hits:
      if len(lst)>0:
        for hit in lst:
          if len(hit)==3:
            referencePeak , targetPeak, position = hit
            newPeakFromReference = referencePeak.copyTo(npl)
            newPeakFromTarget = targetPeak.copyTo(npl)

            newPeakFromReference.annotation = 'Hit'
            newPeakFromTarget.annotation = 'Hit'
            newPeakFromReference.comment = 'Hit: Peak From Reference'
            newPeakFromTarget.comment = 'Hit: Peak From Target'


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: aligned spectra
    '''

    referenceSpectrumGroup = self._getSpectrumGroup(self._kwargs[ReferenceSpectrumGroup])
    wLcontrolSpectrumGroup = self._getSpectrumGroup(self._kwargs[WLcontrolSpectrumGroup])
    wLtargetSpectrumGroup = self._getSpectrumGroup(self._kwargs[WLcontrolSpectrumGroup])

    minimumDistance = float(self._kwargs[MinimumDistance])
    minimumEfficiency = float(self._kwargs[MinimumEfficiency])
    nPeakList = int(self._kwargs[ReferencePeakList])

    mode = self._kwargs[ModeHit]

    if referenceSpectrumGroup and wLtargetSpectrumGroup is not None:

      for targetSpectrum, controlSpectrum in zip(wLtargetSpectrumGroup.spectra, referenceSpectrumGroup.spectra):
        hits = wl.findWaterLogsyHits(wLTarget=targetSpectrum, wLControl=controlSpectrum, mode=mode, limitRange=minimumDistance)
        if len(hits)>0:
          print(hits)
              # self._addNewHit(wLogsySpectrum, hits)

    return spectra

WaterLogsyHitFinderPipe.register() # Registers the pipe in the pipeline


