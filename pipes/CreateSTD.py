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
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.LineEdit import LineEdit

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.AnalysisScreen.lib.experimentAnalysis.STD import spectrumDifference
from ccpn.pipes.lib._new1Dspectrum import _create1DSpectrum


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################

## Widget variables and/or _kwargs keys
OffResonanceSpectrumGroup = 'Off_Resonance_SpectrumGroup'
OnResonanceSpectrumGroup = 'On_Resonance_SpectrumGroup'
NewSTDSpectrumGroupName = 'New_STD_SpectrumGroup_Name'
SGVarNames = [OffResonanceSpectrumGroup, OnResonanceSpectrumGroup]

## defaults
DefaultSTDname = 'STD_'

## PipeName
PipeName = 'STD Creator'


########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################

def _createSTDs(project, offResonanceSpectrumGroup, onResonanceSpectrumGroup):
    spectraSTD = []
    if offResonanceSpectrumGroup and onResonanceSpectrumGroup is not None:
        if len(offResonanceSpectrumGroup.spectra) == len(onResonanceSpectrumGroup.spectra):
            for offResSpectrum, onResSpectrum in zip(offResonanceSpectrumGroup.spectra, onResonanceSpectrumGroup.spectra):
                stdIntensities = spectrumDifference(offResSpectrum, onResSpectrum)
                stdPositions = offResSpectrum.positions

                std = _create1DSpectrum(project=project, name=DefaultSTDname + offResSpectrum.name, intensities=stdIntensities,
                                        positions=stdPositions, expType='STD.H', axisCodes=offResSpectrum.axisCodes)
                spectraSTD.append(std)
    return spectraSTD


########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################


class STDCreatorGuiPipe(GuiPipe):
    preferredPipe = False
    applicationSpecificPipe = True
    pipeName = PipeName

    def __init__(self, name=pipeName, parent=None, project=None, **kwds):
        super(STDCreatorGuiPipe, self)
        GuiPipe.__init__(self, parent=parent, name=name, project=project, **kwds)
        self._parent = parent

        row = 0
        hw._addSGpulldowns(self, row, SGVarNames)
        row += len(SGVarNames)

        self.newSTDSpectrumGroupLabel = Label(self.pipeFrame, NewSTDSpectrumGroupName, grid=(row, 0))
        setattr(self, NewSTDSpectrumGroupName, LineEdit(self.pipeFrame, text=DefaultSTDname, textAlignment='l', hAlign='l', grid=(row, 1)))

        self._updateWidgets()

    def _updateWidgets(self):
        self._setSpectrumGroupPullDowns(SGVarNames)


########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################


class STDCreator(SpectraPipe):
    guiPipe = STDCreatorGuiPipe
    pipeName = PipeName

    _kwargs = {
        OffResonanceSpectrumGroup: 'OffResonanceSpectrumGroup.pid',
        OnResonanceSpectrumGroup: 'OnResonanceSpectrumGroup.pid',
        NewSTDSpectrumGroupName: DefaultSTDname,
        }

    def _createNewSTDspectrumGroup(self, name, stdSpectra):
        newSTDspectrumGroup = None
        if not self.project.getByPid('SG:' + name):
            newSTDspectrumGroup = self.project.newSpectrumGroup(name=name, spectra=stdSpectra)
        else:
            newSTDspectrumGroup = self.project.newSpectrumGroup(name=name + '_new', spectra=stdSpectra)

        if newSTDspectrumGroup is not None:
            return newSTDspectrumGroup

    def runPipe(self, spectra):
        '''
        :param spectra: inputData
        :return: aligned spectra
        '''

        offResonanceSpectrumGroup = self._getSpectrumGroup(self._kwargs[OffResonanceSpectrumGroup])
        onResonanceSpectrumGroup = self._getSpectrumGroup(self._kwargs[OnResonanceSpectrumGroup])
        newSTDSpectrumGroupName = self._kwargs[NewSTDSpectrumGroupName]
        if None not in [offResonanceSpectrumGroup, onResonanceSpectrumGroup, newSTDSpectrumGroupName]:
            stds = _createSTDs(self.project, offResonanceSpectrumGroup, onResonanceSpectrumGroup)
            if len(stds) == len(offResonanceSpectrumGroup.spectra):
                newSTDspectrumGroup = self._createNewSTDspectrumGroup(name=newSTDSpectrumGroupName, stdSpectra=stds)
                if newSTDspectrumGroup is not None:
                    self.spectrumGroups.update([newSTDspectrumGroup])
                    self.project._logger.info("STD SpectrumGroup added on pipeline inputData")
                    self.pipeline.updateInputData = True
                    listsOfSpectra = [onResonanceSpectrumGroup.spectra, offResonanceSpectrumGroup.spectra, newSTDspectrumGroup.spectra]
                    sg_spectra = set([spectrum for listSpectra in listsOfSpectra for spectrum in listSpectra])
                    spectra = set(spectra)
                    spectra.update(sg_spectra)

        return set(spectra)


STDCreator.register()  # Registers the pipe in the pipeline
