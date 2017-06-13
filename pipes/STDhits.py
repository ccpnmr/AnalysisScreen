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
from ccpn.ui.gui.widgets.CheckBox import CheckBox

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.AnalysisScreen.lib.experimentAnalysis.STD import _find_STD_Hits
from scipy import signal
import numpy as np


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
ReferenceSpectrumGroup = 'referenceSpectrumGroup'
STDSpectrumGroup = 'STDSpectrumGroup'

MinimumDistance = 'minimumDistance'
ReferencePeakList = 'referencePeakList'
MinimumEfficiency = 'minimalEfficiency'
CalculateEfficiency = 'calculateEfficiency'
ReferenceSpectrumGroupName = 'References'
OffResonanceSpectrumGroup = 'OffResonanceSpectrumGroup'
OnResonanceSpectrumGroup = 'OnResonanceSpectrumGroup'

## defaults
DefaultEfficiency = 10
DefaultReferencePeakList =  0
DefaultMinimumDistance = 0.01

## PipeName
PipeName = 'STD Hits'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################






########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################




class STDHitFinderGuiPipe(GuiPipe):

  preferredPipe = True
  pipeName = PipeName


  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(STDHitFinderGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent
    row = 0
    self.referenceSpectrumLabel = Label(self.pipeFrame, 'Reference Spectrum Group',  grid=(row,0))
    setattr(self, ReferenceSpectrumGroup, PulldownList(self.pipeFrame,  grid=(row, 1)))

    row += 1
    self.targetSpectrumLabel = Label(self.pipeFrame, 'STD Spectrum Group', grid=(row, 0))
    setattr(self, STDSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.peakListLabel = Label(self.pipeFrame, 'Reference PeakList', grid=(row, 0))
    setattr(self, ReferencePeakList, PulldownList(self.pipeFrame, texts=[str(n) for n in range(5)], grid=(row, 1)))

    row += 1
    self.minimumDistanceLabel = Label(self.pipeFrame, text='Match peaks within (ppm)', grid=(row, 0))
    setattr(self, MinimumDistance,
            LineEdit(self.pipeFrame, text=str(DefaultMinimumDistance), textAligment='l', grid=(row, 1), hAlign='l'))

    row += 1
    self.efficiencyLabel = Label(self.pipeFrame, 'Calculate efficiency', grid=(row, 0))
    setattr(self, CalculateEfficiency, CheckBox(self.pipeFrame, checked=False, callback=self._manageEfficiencyWidgets,
                                                grid=(row, 1), hAlign='l'))


    row += 1
    self.offResonanceLabel = Label(self.pipeFrame, 'Off Resonance Spectrum Group', grid=(row, 0))
    setattr(self, OffResonanceSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.targetSpectrumLabel = Label(self.pipeFrame, 'On Resonance Spectrum Group', grid=(row, 0))
    setattr(self, OnResonanceSpectrumGroup, PulldownList(self.pipeFrame, grid=(row, 1)))

    row += 1
    self.minimalEfficiencyLabel = Label(self.pipeFrame, 'Minimal  Efficiency (%)' , grid=(row, 0))
    setattr(self, MinimumEfficiency, DoubleSpinbox(self.pipeFrame, value=DefaultEfficiency, grid=(row, 1), hAlign='l'))

    _getWidgetByAtt(self, CalculateEfficiency).setEnabled(False)
    self._hideEfficiencyWidgets()
    self._updateInputDataWidgets()

  def _updateInputDataWidgets(self):
    self._setDataPullDowns()


  def _setDataPullDowns(self):
    spectrumGroups = list(self.spectrumGroups)
    if len(spectrumGroups)>0:
      _getWidgetByAtt(self, ReferenceSpectrumGroup).setData(texts=[sg.pid for sg in spectrumGroups], objects=spectrumGroups)
      _getWidgetByAtt(self, STDSpectrumGroup).setData(texts=[sg.pid for sg in spectrumGroups], objects=spectrumGroups)

      # trying to select reference spectrum group in the correct pulldown by matching name
      for sg in spectrumGroups:
        if ReferenceSpectrumGroupName in sg.name:
          _getWidgetByAtt(self, ReferenceSpectrumGroup).select(sg)
    else:
      _getWidgetByAtt(self, ReferenceSpectrumGroup)._clear()
      _getWidgetByAtt(self, STDSpectrumGroup)._clear()

  def _hideEfficiencyWidgets(self):
    self.offResonanceLabel.hide()
    self.targetSpectrumLabel.hide()
    self.minimalEfficiencyLabel.hide()
    _getWidgetByAtt(self, OffResonanceSpectrumGroup).hide()
    _getWidgetByAtt(self, OnResonanceSpectrumGroup).hide()
    _getWidgetByAtt(self, MinimumEfficiency).hide()

  def _showEfficiencyWidgets(self):
    self.offResonanceLabel.show()
    self.targetSpectrumLabel.show()
    self.minimalEfficiencyLabel.show()
    _getWidgetByAtt(self, OffResonanceSpectrumGroup).show()
    _getWidgetByAtt(self, OnResonanceSpectrumGroup).show()
    _getWidgetByAtt(self, MinimumEfficiency).show()

  def _manageEfficiencyWidgets(self):
    checkbox = _getWidgetByAtt(self, CalculateEfficiency)
    if checkbox.isChecked():
      self._showEfficiencyWidgets()
    else:
      self._hideEfficiencyWidgets()







########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class STDHitFinder(SpectraPipe):

  guiPipe = STDHitFinderGuiPipe
  pipeName = PipeName

  _kwargs  =   {
                ReferenceSpectrumGroup: 'spectrumGroup.pid',
                STDSpectrumGroup:       'spectrumGroup.pid',
                OffResonanceSpectrumGroup: 'OffResonanceSpectrumGroup.pid',
                OnResonanceSpectrumGroup: 'OnResonanceSpectrumGroup.pid',
                MinimumDistance:         DefaultMinimumDistance,
                MinimumEfficiency:       DefaultEfficiency,
                ReferencePeakList:       DefaultReferencePeakList,
               }

  def _addNewHit(self, spectrum, hits):
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
    stdSpectrumGroup = self._getSpectrumGroup(self._kwargs[STDSpectrumGroup])
    minimumDistance = float(self._kwargs[MinimumDistance])
    minimumEfficiency = float(self._kwargs[MinimumEfficiency])
    nPeakList = int(self._kwargs[ReferencePeakList])

    if referenceSpectrumGroup and stdSpectrumGroup is not None:
      for stdSpectrum in stdSpectrumGroup.spectra:
        if stdSpectrum:
          hits = _find_STD_Hits(stdSpectrum=stdSpectrum,referenceSpectra=referenceSpectrumGroup.spectra, limitRange=minimumDistance)

          if len(hits)>0:
            self._addNewHit(stdSpectrum, hits)

    return spectra

STDHitFinder.register() # Registers the pipe in the pipeline


