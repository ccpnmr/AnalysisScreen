
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
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:14 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================



from collections import OrderedDict
from ccpn.ui.gui.modules.PipelineModule import GuiPipeline
import os
# from ccpn.AnalysisMetabolomics import GuiPipeLine as gp


pipelineFilesDirName = '/guiPipeline/'
templates =   OrderedDict((
                          ('Wlogsy', 'WlogsyTemplate'),
                          ('STD', 'STDTemplate'),
                          ('Broadening1H', 'Broadening1HTemplate'),
                          ('t1Rho', 't1RhoTemplate'),
                         ))


def initialiseScreeningPipelineModule(mainWindow):
  from ccpn.AnalysisScreen import guiPipeline as _pm
  pipelineMethods = _pm.__all__
  guiPipeline= GuiPipeline(mainWindow=mainWindow, pipelineMethods=pipelineMethods, templates=templates)
  mainWindow.moduleArea.addModule(guiPipeline, position='bottom')