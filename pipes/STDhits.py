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
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe , _getWidgetByAtt
from ccpn.AnalysisScreen.gui.widgets import HitFinderWidgets as hw

#### NON GUI IMPORTS
from ccpn.framework.lib.Pipe import SpectraPipe
from ccpn.AnalysisScreen.lib.experimentAnalysis.STD import _find_STD_Hits
from ccpn.AnalysisScreen.lib.experimentAnalysis.NewHit import _addNewHit, _getReferencesFromSample
from ccpn.util.Logging import getLogger , _debug3

########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
ReferenceSpectrumGroup = 'Reference_SpectrumGroup'
STD_Control_SpectrumGroup = 'STD_Control_SpectrumGroup'
STD_Target_SpectrumGroup = 'STD_Target_SpectrumGroup'
SC_as_Refs = 'Use_SampleComponents_as_References'
SGVarNames = [STD_Control_SpectrumGroup, STD_Target_SpectrumGroup, ReferenceSpectrumGroup]

MatchPeaksWithin = 'Match_Peaks_Within_(ppm)'
RefPLIndex = 'Reference_PeakList'
TargetPeakListIndex = 'Target_PeakList'
MinEfficiency = 'Minimal_Efficiency'

## defaults
DefaultEfficiency = 7
DefaultMinDist = 0.01
DefaultPeakListIndex = -1

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

  preferredPipe = False
  applicationSpecificPipe = True
  pipeName = PipeName


  def __init__(self, name=pipeName, parent=None, project=None,   **kwds):
    super(STDHitFinderGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kwds)
    self._parent = parent

    row = 0
    hw._addSGpulldowns(self, row, SGVarNames)

    row += len(SGVarNames)
    hw._addCommonHitFinderWidgets(self, row, ReferenceSpectrumGroup, SC_as_Refs,
                                  MatchPeaksWithin, DefaultMinDist,
                                  MinEfficiency, DefaultEfficiency)

    self._updateWidgets()


  def _updateWidgets(self):
    self._setSpectrumGroupPullDowns(SGVarNames, headerText='None',headerEnabled=True,)







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
                SC_as_Refs:       False,
                MatchPeaksWithin:           DefaultMinDist,
                MinEfficiency:              DefaultEfficiency,

               }


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: same spectra after finding hits. The spectra should be the same
    '''
    controlSpectrumGroup = self._getSpectrumGroup(self._kwargs[STD_Control_SpectrumGroup])
    referenceSpectrumGroup = self._getSpectrumGroup(self._kwargs[ReferenceSpectrumGroup])
    stdTargetSpectrumGroup = self._getSpectrumGroup(self._kwargs[STD_Target_SpectrumGroup])
    sampleComponents_as_References = self._kwargs[SC_as_Refs]
    minimumDistance = float(self._kwargs[MatchPeaksWithin])
    minimumEfficiency = float(self._kwargs[MinEfficiency])/100


    references = []
    if stdTargetSpectrumGroup is not None:
      if set(stdTargetSpectrumGroup.spectra).issubset(spectra): # make sure spectrumGroup.spectra are in the input spectra
        if controlSpectrumGroup is None:
          controlSpectra = [None]*len(stdTargetSpectrumGroup.spectra)
        else:
          controlSpectra = controlSpectrumGroup.spectra
        for stdSpectrum, controlSTD in zip(stdTargetSpectrumGroup.spectra,controlSpectra) :
          if stdSpectrum:
            if stdSpectrum.experimentType is None:
              stdSpectrum.experimentType = 'STD.H'
            if sampleComponents_as_References:
              references = _getReferencesFromSample(stdSpectrum)
            else:
              if referenceSpectrumGroup is not None:
                if set(referenceSpectrumGroup.spectra).issubset(spectra):
                  references = referenceSpectrumGroup.spectra #make sure references are in the input spectra
            if len(stdSpectrum.peakLists)>0:
              listsTargetHits = _find_STD_Hits(stdSpectrum=stdSpectrum,referenceSpectra=references, limitRange=minimumDistance,
                                    refPeakListIndex=DefaultPeakListIndex,  minEfficiency=minimumEfficiency )

              if controlSTD is not None:
                listsControlHits = _find_STD_Hits(stdSpectrum=controlSTD, referenceSpectra=references,
                                          limitRange=minimumDistance,
                                          refPeakListIndex=DefaultPeakListIndex, minEfficiency=minimumEfficiency)
              else:
                listsControlHits  = []
              targetHits = [i for hit in listsTargetHits for i in hit] # clean up the empty sublists
              controlHits = [i for hit in listsControlHits for i in hit]  # clean up the empty sublists
              filteredHits = self._filterFalsePositiveHits(targetHits, controlHits)
              if len(filteredHits)>0:
                _addNewHit(stdSpectrum, filteredHits)

    else:
      getLogger().warning('Aborted: STD SpectrumGroup not found')
    # TODO this should return the spectrumHits only
    SGSpectra = [sp for sg in self.spectrumGroups if sg is not None for sp in sg.spectra]
    return set(list(spectra)+SGSpectra)



  def _filterFalsePositiveHits(self, targetHits, controlHits, limitRange=0.01):
    ''' 
    Checks if the same hit is present in the control spectrum
    '''
    falsePositivePositions = set()
    falsePositives = []

    for controlHit in controlHits:
      if len(controlHit) == 3:
        referencePeak, controlPeak, controlPosition = controlHit
        falsePositivePositions.update((controlPosition[0][0],))

    for falsePositivePosition in list(falsePositivePositions):
      falsePositives += [ hit for hit in targetHits if abs(falsePositivePosition-hit[2][0][0]) <= limitRange]

    targetHits = [hit for hit in targetHits if hit not in falsePositives ]
    return targetHits



STDHitFinder.register() # Registers the pipe in the pipeline


