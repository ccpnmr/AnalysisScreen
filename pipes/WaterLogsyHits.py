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
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw

#### NON GUI IMPORTS
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
ReferenceFromMixture = 'Reference_from_Mixture'
TargetSpectrumGroup    = 'WL_Target_SpectrumGroup'
ControlSpectrumGroup   = 'WL_Control_SpectrumGroup'
SGVarNames = [ControlSpectrumGroup, TargetSpectrumGroup, ReferenceSpectrumGroup]

MatchPeaksWithin  =  'Match_Peaks_Within_(ppm)'
RefPL = 'Reference_PeakList'
MinEfficiency = 'Minimal_Efficiency'
ModeHit = 'Finding_Mode'

## defaults
DefaultEfficiency = 10
DefaultReferencePeakList =  0
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

  preferredPipe = True
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
    hw._addCommonHitFinderWidgets(self, row, ReferenceSpectrumGroup, ReferenceFromMixture, RefPL, MatchPeaksWithin,
                                  DefaultMinDist, MinEfficiency, DefaultEfficiency)

    self._updateWidgets()

  def _updateWidgets(self):
    self._setSpectrumGroupPullDowns(SGVarNames)
    self._setMaxValueRefPeakList(RefPL)


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
                ReferenceFromMixture:    False,
                MatchPeaksWithin:        DefaultMinDist,
                MinEfficiency:           MinEfficiency,
                RefPL:                   DefaultReferencePeakList,
               }


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: aligned spectra
    '''

    referenceSpectrumGroup = self._getSpectrumGroup(self._kwargs[ReferenceSpectrumGroup])
    wLcontrolSpectrumGroup = self._getSpectrumGroup(self._kwargs[ControlSpectrumGroup])
    wLtargetSpectrumGroup = self._getSpectrumGroup(self._kwargs[TargetSpectrumGroup])
    referenceFromMixture = self._kwargs[ReferenceFromMixture]

    minimumDistance = float(self._kwargs[MatchPeaksWithin])
    minimumEfficiency = float(self._kwargs[MinEfficiency])
    nPeakList = int(self._kwargs[RefPL])

    mode = self._kwargs[ModeHit]
    references = []

    if wLcontrolSpectrumGroup is None: # if no control is given. Find hits just by positive peaks in the target spectrum
      mode = wl.PositiveOnly

      if wLtargetSpectrumGroup is not None:
        for targetSpectrum in wLtargetSpectrumGroup.spectra:
          if targetSpectrum is not None:
            if targetSpectrum.experimentType is None:
              targetSpectrum.experimentType = 'Water-LOGSY.H'

            if referenceFromMixture:
              references = _getReferencesFromSample(targetSpectrum)
            else:
              if referenceSpectrumGroup is not None:
                references = referenceSpectrumGroup.spectra

              hits = wl.findWaterLogsyHits(wLTarget=targetSpectrum, mode=mode, limitRange=minimumDistance)
              if len(hits) > 0:
                # _addNewHit(targetSpectrum, hits)
                matchedRef = matchHitToReference(targetSpectrum, references, limitRange=minimumDistance,
                                                 peakListIndex=nPeakList)
                matchedRef = [i for hit in matchedRef for i in hit]  # clean up the empty sublists
                if len(matchedRef) > 0:
                  _addNewHit(targetSpectrum, matchedRef)


    else:# if control is given. Find hits  by any mode
      if wLtargetSpectrumGroup is not None:
        if len(wLtargetSpectrumGroup.spectra) == len(wLcontrolSpectrumGroup.spectra):
          for targetSpectrum, controlSpectrum in zip(wLtargetSpectrumGroup.spectra, wLcontrolSpectrumGroup.spectra):
            if targetSpectrum is not None:
              if targetSpectrum.experimentType is None:
                targetSpectrum.experimentType = 'Water-LOGSY.H'

              if referenceFromMixture:
                references = _getReferencesFromSample(targetSpectrum)
              else:
                if referenceSpectrumGroup is not None:
                  references = referenceSpectrumGroup.spectra

              hits = wl.findWaterLogsyHits(wLTarget=targetSpectrum, wLControl=controlSpectrum,
                                           mode=mode, limitRange=minimumDistance)
              hits = [i for hit in hits for i in hit]  # clean up the empty sublists
              if len(hits) > 0:
                # _addNewHit(targetSpectrum, hits)
                matchedRef = matchHitToReference(targetSpectrum, references, limitRange=minimumDistance,
                                                 peakListIndex=nPeakList)
                matchedRef = [i for hit in matchedRef for i in hit]  # clean up the empty sublists
                if len(matchedRef) > 0:
                  _addNewHit(targetSpectrum, matchedRef)


    return spectra

WaterLogsyHitFinderPipe.register() # Registers the pipe in the pipeline


