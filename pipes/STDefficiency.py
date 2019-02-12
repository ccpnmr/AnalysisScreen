#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2019"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Luca Mureddu $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:26 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b5 $"
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
from ccpn.AnalysisScreen.lib.experimentAnalysis.STD import _calculatePeakEfficiency
from ccpn.util.Logging import getLogger, _debug3


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
OffResonanceSpectrumGroup = 'Off_Resonance_SpectrumGroup'
OnResonanceSpectrumGroup = 'On_Resonance_SpectrumGroup'
STDSpectrumGroup = 'STD_SpectrumGroup'
SGVarNames = [OffResonanceSpectrumGroup, OnResonanceSpectrumGroup, STDSpectrumGroup]
RefPL = 'Reference_PeakList'
MatchPeaksWithin = 'Match_Peaks_Within_(ppm)'

## defaults
DefaultMinDist = 0.01
DefaultPeakListIndex = -1

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
    preferredPipe = False
    applicationSpecificPipe = True
    pipeName = PipeName

    def __init__(self, name=pipeName, parent=None, project=None, **kwds):
        super(STDEfficiencyGuiPipe, self)
        GuiPipe.__init__(self, parent=parent, name=name, project=project, **kwds)
        self._parent = parent

        row = 0
        hw._addSGpulldowns(self, row, SGVarNames)

        row += len(SGVarNames)
        minimumDistanceLabel = Label(self.pipeFrame, MatchPeaksWithin, grid=(row, 0))
        setattr(self, MatchPeaksWithin, DoubleSpinbox(self.pipeFrame, value=DefaultMinDist,
                                                      step=DefaultMinDist, min=0.01, grid=(row, 1)))

        self._updateWidgets()

    def _updateWidgets(self):
        self._setSpectrumGroupPullDowns(SGVarNames)


########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################


class STDEfficiencyPipe(SpectraPipe):
    guiPipe = STDEfficiencyGuiPipe
    pipeName = PipeName

    _kwargs = {
        OffResonanceSpectrumGroup: 'OffResonanceSpectrumGroup.pid',
        OnResonanceSpectrumGroup: 'OnResonanceSpectrumGroup.pid',
        STDSpectrumGroup: 'STDSpectrumGroup.pid',
        MatchPeaksWithin: DefaultMinDist,
        }

    def runPipe(self, spectra):
        '''
        :param spectra: inputData
        :return: calculates the STD peak efficiency and stores the value in the peak.figureOfMerit.
        '''

        stdSpectrumGroup = self._getSpectrumGroup(self._kwargs[STDSpectrumGroup])
        offResonanceSpectrumGroup = self._getSpectrumGroup(self._kwargs[OffResonanceSpectrumGroup])
        onResonanceSpectrumGroup = self._getSpectrumGroup(self._kwargs[OnResonanceSpectrumGroup])

        minimumDistance = float(self._kwargs[MatchPeaksWithin])

        if None in [stdSpectrumGroup, offResonanceSpectrumGroup, onResonanceSpectrumGroup]:
            getLogger().warning('Aborted: SpectrumGroup spectra contains illegal values (None)')
            return
        if len(stdSpectrumGroup.spectra) == len(offResonanceSpectrumGroup.spectra) == len(onResonanceSpectrumGroup.spectra):
            for stdSpectrum, offResonanceSpectrum, onResonanceSpectrum in zip(
                    stdSpectrumGroup.spectra, offResonanceSpectrumGroup.spectra, onResonanceSpectrumGroup.spectra):
                _calculatePeakEfficiency(stdSpectrum, onResonanceSpectrum, offResonanceSpectrum, n_peakList=DefaultPeakListIndex,
                                         limitRange=minimumDistance)
            self.project._logger.info('Peak efficiency calculated and stored in peak "figureOfMerit" ')
        else:
            getLogger().warning('Aborted: SpectrumGroups contain different lenght of spectra.')

        return set(spectra)


STDEfficiencyPipe.register()  # Registers the pipe in the pipeline
