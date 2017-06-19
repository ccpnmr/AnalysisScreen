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
from scipy import signal
import numpy as np


########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys
ReferenceSpectrumGroup = 'Reference_SpectrumGroup'
STD_Control_SpectrumGroup = 'STD_Control_SpectrumGroup'
STD_Target_SpectrumGroup = 'STD_Target_SpectrumGroup'
SGVarNames = [ReferenceSpectrumGroup, STD_Control_SpectrumGroup, STD_Target_SpectrumGroup]

MatchPeaksWithin = 'Match_Peaks_Within_(ppm)'
RefPL = 'Reference_PeakList'
MinEfficiency = 'Minimal_Efficiency'

## defaults
DefaultEfficiency = 10
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
    hw._addCommonHitFinderWidgets(self, row, RefPL, MatchPeaksWithin, DefaultMinDist, MinEfficiency, DefaultEfficiency)

    self._updateInputDataWidgets()


  def _updateInputDataWidgets(self):
    self._setSpectrumGroupPullDowns(SGVarNames)
    self._setMaxValueRefPeakList(RefPL)







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
                MatchPeaksWithin:           DefaultMinDist,
                MinEfficiency:              DefaultEfficiency,
                RefPL:                      DefaultReferencePeakList,
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
    stdTargetSpectrumGroup = self._getSpectrumGroup(self._kwargs[STD_Target_SpectrumGroup])

    minimumDistance = float(self._kwargs[MatchPeaksWithin])
    minimumEfficiency = float(self._kwargs[MinEfficiency])
    nPeakList = int(self._kwargs[RefPL])

    if referenceSpectrumGroup and stdTargetSpectrumGroup is not None:
      for stdSpectrum in stdTargetSpectrumGroup.spectra:
        if stdSpectrum:
          hits = _find_STD_Hits(stdSpectrum=stdSpectrum,referenceSpectra=referenceSpectrumGroup.spectra, limitRange=minimumDistance)

          if len(hits)>0:
            self._addNewHit(stdSpectrum, hits)

    return spectra

STDHitFinder.register() # Registers the pipe in the pipeline


