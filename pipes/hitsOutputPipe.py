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
__version__ = "$Revision: 3.0.b3 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-05-28 10:28:42 +0000 (Sun, May 28, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================



#################################################
#######   NOT IMPLEMENTED YET      ##############
#################################################








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

########################################################################################################################
###   Attributes:
###   Used in setting the dictionary keys on _kwargs either in GuiPipe and Pipe
########################################################################################################################


## Widget variables and/or _kwargs keys


## defaults


## PipeName
PipeName = 'Output Hits'



########################################################################################################################
##########################################     GUI PIPE    #############################################################
########################################################################################################################


class OutputHitsGuiPipe(GuiPipe):
  
  preferredPipe = False
  applicationSpecificPipe = True
  pipeName = PipeName
  _alreadyOpened = False


  def __init__(self, name=pipeName, parent=None, project=None, **kwds):
    super(OutputHitsGuiPipe, self)
    GuiPipe.__init__(self, parent=parent, name=name, project=project, **kwds)
    self._parent = parent
    OutputHitsGuiPipe._alreadyOpened = True




  def _closeBox(self):
    'reset alreadyOpened flag '
    OutputHitsGuiPipe._alreadyOpened = False
    self.closeBox()




########################################################################################################################
##########################################       PIPE      #############################################################
########################################################################################################################




class OutputHitsPipe(SpectraPipe):

  guiPipe = OutputHitsGuiPipe
  pipeName = PipeName

  _kwargs  =   {

               }


  def runPipe(self, spectra):
    '''
    :param spectra: inputData
    :return: spectra
    '''

    return spectra

# OutputHitsPipe.register() # Registers the pipe in the pipeline


