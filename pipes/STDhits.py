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
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.AnalysisScreen.lib.experimentAnalysis.STD import _find_STD_Hits
from ccpn.AnalysisScreen.lib.experimentAnalysis.NewHit import _addNewHit, _getReferencesFromSample

########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
ReferenceSpectrumGroup = 'Reference_SpectrumGroup'
STD_Control_SpectrumGroup = 'STD_Control_SpectrumGroup'
STD_Target_SpectrumGroup = 'STD_Target_SpectrumGroup'
ReferenceFromMixture = 'Reference_from_Mixture'
SGVarNames = [STD_Target_SpectrumGroup, ReferenceSpectrumGroup]

MatchPeaksWithin = 'Match_Peaks_Within_(ppm)'
RefPLIndex = 'Reference_PeakList'
TargetPeakListIndex = 'Target_PeakList'
MinEfficiency = 'Minimal_Efficiency'

## defaults
DefaultEfficiency = 7
DefaultMinDist = 0.01
DefaultReferencePeakList = 0

## PipeName
PipeName = 'STD Hits'

########################################################################################################################
##########################################      ALGORITHM       ########################################################
########################################################################################################################

## See AnalysisScreen Lib

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
    hw._addSGpulldowns(self, row, SGVarNames)

    row += len(SGVarNames)
    hw._addCommonHitFinderWidgets(self, row, ReferenceSpectrumGroup, ReferenceFromMixture, RefPLIndex, TargetPeakListIndex, MatchPeaksWithin, DefaultMinDist,
                                  MinEfficiency, DefaultEfficiency)

    self._updateWidgets()


  def _updateWidgets(self):
    self._setSpectrumGroupPullDowns(SGVarNames)
    self._setMaxValueRefPeakList(RefPLIndex)







########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class STDHitFinder(SpectraPipe):

  guiPipe = STDHitFinderGuiPipe
  pipeName = PipeName

  _kwargs  =   {
                ReferenceSpectrumGroup:     'spectrumGroup.pid',
                STD_Control_SpectrumGroup:  'spectrumGroup.pid',
                STD_Target_SpectrumGroup:   'spectrumGroup.pid',
                ReferenceFromMixture:       False,
                MatchPeaksWithin:           DefaultMinDist,
                MinEfficiency:              DefaultEfficiency,
                RefPLIndex:                 DefaultReferencePeakList,

               }


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: same spectra after finding hits. The spectra should be the same
    '''
    referenceSpectrumGroup = self._getSpectrumGroup(self._kwargs[ReferenceSpectrumGroup])
    stdTargetSpectrumGroup = self._getSpectrumGroup(self._kwargs[STD_Target_SpectrumGroup])
    referenceFromMixture = self._kwargs[ReferenceFromMixture]
    minimumDistance = float(self._kwargs[MatchPeaksWithin])
    minimumEfficiency = float(self._kwargs[MinEfficiency])/100
    refPeakListIndex = int(self._kwargs[RefPLIndex])
    targPeakListIndex = int(self._kwargs[TargetPeakListIndex])

    references = []
    if stdTargetSpectrumGroup is not None:
      if set(stdTargetSpectrumGroup.spectra).issubset(spectra): # make sure spectrumGroup.spectra are in the input spectra
        for stdSpectrum in stdTargetSpectrumGroup.spectra:
          if stdSpectrum:
            if stdSpectrum.experimentType is None:
              stdSpectrum.experimentType = 'STD.H'
            if referenceFromMixture:
              references = _getReferencesFromSample(stdSpectrum)
            else:
              if referenceSpectrumGroup is not None:
                if set(referenceSpectrumGroup.spectra).issubset(spectra):
                  references = referenceSpectrumGroup.spectra #make sure references are in the input spectra
            hits = _find_STD_Hits(stdSpectrum=stdSpectrum,referenceSpectra=references, limitRange=minimumDistance,
                                  refPeakListIndex=refPeakListIndex,  minEfficiency=minimumEfficiency )
            hits = [i for hit in hits for i in hit] # clean up the empty sublists
            if len(hits)>0:
              _addNewHit(stdSpectrum, hits)

    SGSpectra = [sp for sg in self.spectrumGroups if sg is not None for sp in sg.spectra]
    return list(set(list(spectra)+SGSpectra))


STDHitFinder.register() # Registers the pipe in the pipeline


