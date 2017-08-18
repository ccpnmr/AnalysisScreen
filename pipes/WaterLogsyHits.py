#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:26 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b2 $"
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
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw

#### NON GUI IMPORTS
import numpy as np
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.AnalysisScreen.lib.experimentAnalysis import WaterLogsy as wl
from ccpn.AnalysisScreen.lib.experimentAnalysis.NewHit import _addNewHit, _getReferencesFromSample
from ccpn.AnalysisScreen.lib.experimentAnalysis.MatchPositions import  matchHitToReference
########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
ReferenceSpectrumGroup = 'Reference_SpectrumGroup'
SCasRef = 'Use_SampleComponents_as_References'
TargetSpectrumGroup    = 'WL_Target_SpectrumGroup'
ControlSpectrumGroup   = 'WL_Control_SpectrumGroup'
SGVarNames = [ControlSpectrumGroup, TargetSpectrumGroup, ReferenceSpectrumGroup]

MatchPeaksWithin  =  'Match_Peaks_Within_(ppm)'
RefPLIndex = 'Reference_PeakList'
TargetPeakListIndex = 'Target_PeakList'
MinEfficiency = 'Minimal_Intensity_Change'
ModeHit = 'Finding_Mode'

## defaults
DefaultEfficiency = 10
DefaultPeakListIndex = -1
DefaultMinDist = 0.01

## PipeName
PipeName = 'WaterLogsy Hits'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################

## See AnalysisScreen Lib

########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################


class WaterLogsyHitFinderGuiPipe(GuiPipe):

  preferredPipe = False
  applicationSpecificPipe = True
  pipeName = PipeName


  def __init__(self, name=pipeName, parent=None, project=None,   **kw):
    super(WaterLogsyHitFinderGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kw )
    self.parent = parent

    row = 0
    self.modeLabel = Label(self.pipeFrame, ModeHit, grid=(row, 0))
    setattr(self, ModeHit, PulldownList(self.pipeFrame, texts=wl.MODES, callback=self._modeCallback, grid=(row, 1)))

    row += 1
    hw._addSGpulldowns(self, row, SGVarNames)

    row += len(SGVarNames)
    hw._addCommonHitFinderWidgets(self, row, ReferenceSpectrumGroup, SCasRef, MatchPeaksWithin,
                                  DefaultMinDist, MinEfficiency, DefaultEfficiency)

    self._updateWidgets()

  def _updateWidgets(self):
    self._setSpectrumGroupPullDowns(SGVarNames)


  def _modeCallback(self, selected):
    'manages the spectrumgroups pullDown'
    if selected == wl.PositiveOnly:
      _getWidgetByAtt(self, ControlSpectrumGroup).setEnabled(False)
      _getWidgetByAtt(self, ControlSpectrumGroup)._clear()
    elif selected == wl.IntensityChanged or selected == wl.SignChanged:
      _getWidgetByAtt(self, ControlSpectrumGroup).setEnabled(True)


########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################


class WaterLogsyHitFinderPipe(SpectraPipe):

  guiPipe = WaterLogsyHitFinderGuiPipe
  pipeName = PipeName

  _kwargs  =   {
                ReferenceSpectrumGroup:  'spectrumGroup.pid',
                TargetSpectrumGroup:     'spectrumGroup.pid',
                ControlSpectrumGroup:    'spectrumGroup.pid',
                SCasRef:                  False,
                MatchPeaksWithin:        DefaultMinDist,
                MinEfficiency:           MinEfficiency,
               }


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: spectra. Add Hits to project
    '''
    referenceSpectrumGroup = self._getSpectrumGroup(self._kwargs[ReferenceSpectrumGroup])
    wLcontrolSpectrumGroup = self._getSpectrumGroup(self._kwargs[ControlSpectrumGroup])
    wLtargetSpectrumGroup = self._getSpectrumGroup(self._kwargs[TargetSpectrumGroup])
    minimumDistance = float(self._kwargs[MatchPeaksWithin])
    references = []
    if wLtargetSpectrumGroup is not None:
      targetSpectra = wLtargetSpectrumGroup.spectra
      if wLcontrolSpectrumGroup is None:  # if no control is given. Find hits just by positive peaks in the target spectrum
        controlSpectra = [None] * len(targetSpectra)
        mode = wl.PositiveOnly
      else:
        controlSpectra = wLcontrolSpectrumGroup.spectra
        mode = self._kwargs[ModeHit]

      if len(controlSpectra) == len(targetSpectra):
        for targetSpectrum, controlSpectrum in zip(targetSpectra, controlSpectra):
          if targetSpectrum.experimentType is None:
            targetSpectrum.experimentType = 'Water-LOGSY.H'
          if self._kwargs[SCasRef]: # sampleComponents as References
            references = _getReferencesFromSample(targetSpectrum)
          else:
            if referenceSpectrumGroup is not None:
              references = referenceSpectrumGroup.spectra
          hits = wl.findWaterLogsyHits(wLTarget=targetSpectrum, wLControl=controlSpectrum,
                mode=mode, limitRange=minimumDistance, limitIntensityChange=float(self._kwargs[MinEfficiency]))
          self._filterNewHits(hits, targetSpectrum, references, minimumDistance)

    SGSpectra = [sp for sg in self.spectrumGroups if sg is not None for sp in sg.spectra]
    return set(list(spectra) + SGSpectra)

  def _filterNewHits(self, hits, targetSpectrum, references, minimumDistance):
    if len(hits) > 0:
      if len(targetSpectrum.peakLists) > 0:
        matchedRef = matchHitToReference(targetSpectrum, references, limitRange=minimumDistance,
                                         refPeakListIndex=DefaultPeakListIndex)
        matchedRef = [i for hit in matchedRef for i in hit]  # clean up the empty sublists
        matchedHit = []
        for i in matchedRef:
          if len(i) == 3:
            rp, tp, pos_i = i
            for j in hits:
              if len(j) == 3:
                rp, tp, pos_j = j
                if type(pos_i) is np.ndarray:
                  pos_i = pos_i.ravel()
                  if len(pos_i) > 0:
                    pos_i = pos_i[-1]

                if float(pos_j) == float(pos_i):
                  matchedHit.append(i)
        if len(matchedHit) > 0:
          _addNewHit(targetSpectrum, matchedHit)

WaterLogsyHitFinderPipe.register() # Registers the pipe in the pipeline


