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
__version__ = "$Revision: 3.0.b4 $"
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
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw

#### NON GUI IMPORTS
import numpy as np
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.AnalysisScreen.lib.experimentAnalysis.LineBroadening import findBroadenedPeaks
from ccpn.AnalysisScreen.lib.experimentAnalysis.MatchPositions import matchHitToReference
from ccpn.AnalysisScreen.lib.experimentAnalysis.NewHit import _addNewHit, _getReferencesFromSample


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
ReferenceSpectrumGroup = 'Reference_SpectrumGroup'

SCasRefs = 'Use_SampleComponents_as_References'
TargetSpectrumGroup = 'Target_SpectrumGroup'
ControlSpectrumGroup = 'Control_SpectrumGroup'
SGVarNames = [ControlSpectrumGroup, TargetSpectrumGroup, ReferenceSpectrumGroup]

MatchPeaksWithin = 'Match_Peaks_Within_(ppm)'
RefPLIndex = 'Reference_PeakList'
TargetPeakListIndex = 'Target_PeakList'
MinLWvariation = 'Minimal_Volume_Variation(Ratio)'

## defaults
DefaultMinimalLW = 0.50
DefaultPeakListIndex = -1
DefaultMinimumDistance = 0.01

## PipeName
PipeName = 'Peak Broadening Hit Finder'


########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################

## See AnalysisScreen Lib

########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################


class PeakBroadeningFinderGuiPipe(GuiPipe):
    preferredPipe = False
    applicationSpecificPipe = True
    pipeName = PipeName

    def __init__(self, name=pipeName, parent=None, project=None, **kwds):
        super(PeakBroadeningFinderGuiPipe, self)
        GuiPipe.__init__(self, parent=parent, name=name, project=project, **kwds)
        self._parent = parent

        row = 0
        hw._addSGpulldowns(self, row, SGVarNames)
        row += len(SGVarNames)
        hw._addCommonHitFinderWidgets(self, row, ReferenceSpectrumGroup, SCasRefs,
                                      MatchPeaksWithin, DefaultMinimumDistance, MinLWvariation, DefaultMinimalLW)
        self._updateWidgets()

    def _updateWidgets(self):
        'CCPN internal. Called from gui Pipeline when the input data has changed'
        self._setSpectrumGroupPullDowns(SGVarNames)


########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################


class PeakBroadeningFinder(SpectraPipe):
    guiPipe = PeakBroadeningFinderGuiPipe
    pipeName = PipeName

    _kwargs = {
        ReferenceSpectrumGroup: 'spectrumGroup.pid',
        TargetSpectrumGroup: 'spectrumGroup.pid',
        MatchPeaksWithin: DefaultMinimumDistance,
        MinLWvariation: DefaultMinimalLW,
        TargetPeakListIndex: 1,
        SCasRefs: False,
        }

    def runPipe(self, spectra):
        '''
        :param spectra: inputData
        :return: aligned spectra
        '''

        referenceSpectrumGroup = self._getSpectrumGroup(self._kwargs[ReferenceSpectrumGroup])
        controlSpectrumGroup = self._getSpectrumGroup(self._kwargs[ControlSpectrumGroup])
        targetSpectrumGroup = self._getSpectrumGroup(self._kwargs[TargetSpectrumGroup])
        minimumDistance = float(self._kwargs[MatchPeaksWithin])
        minLWvariation = float(self._kwargs[MinLWvariation])
        sampleComponents_as_References = self._kwargs[SCasRefs]
        references = []

        if controlSpectrumGroup and targetSpectrumGroup is not None:
            if len(controlSpectrumGroup.spectra) == len(targetSpectrumGroup.spectra):
                for controlSpectrum, targetSpectrum in zip(controlSpectrumGroup.spectra, targetSpectrumGroup.spectra):
                    if targetSpectrum:
                        if targetSpectrum.experimentType is None:
                            targetSpectrum.experimentType = 'H'
                        if sampleComponents_as_References:
                            references = _getReferencesFromSample(targetSpectrum)
                        else:
                            if referenceSpectrumGroup is not None:
                                references = referenceSpectrumGroup.spectra

                        ## 'First find hits by broadening'
                        if len(controlSpectrum.peakLists) > 0:
                            targetHits = findBroadenedPeaks(controlSpectrum, targetSpectrum, minimalDiff=minLWvariation,
                                                            limitRange=minimumDistance, targetPLIndex=DefaultPeakListIndex)
                            ## 'Second match TargetPeak ToReference '
                            if len(targetHits) > 0:
                                if len(targetSpectrum.peakLists) > 0:
                                    matchedRef = matchHitToReference(targetSpectrum, references, limitRange=minimumDistance,
                                                                     refPeakListIndex=DefaultPeakListIndex)  #1

                                    matchedHit = []
                                    matchedRef = [i for hit in matchedRef for i in hit]
                                    for i in matchedRef:
                                        if len(i) == 3:
                                            rp, tp, pos_i = i
                                            for j in targetHits:
                                                if len(j) == 3:
                                                    rp, tp, pos_j = j
                                                    if type(pos_i) is np.ndarray:
                                                        pos_i = pos_i.ravel()
                                                        if len(pos_i) > 0:
                                                            pos_i = pos_i[-1]
                                                    if abs(float(pos_i) - float(pos_j)) <= 0.01:
                                                        matchedHit.append(i)

                                    if len(matchedHit) > 0:
                                        _addNewHit(targetSpectrum, matchedHit)

        SGSpectra = [sp for sg in self.spectrumGroups if sg is not None for sp in sg.spectra]
        return set(list(spectra) + SGSpectra)

# PeakBroadeningFinder.register() # Registers the pipe in the pipeline
