
from PyQt4 import QtGui


class Display1DWidget(QtGui.QFrame):
  def __init__(self, parent=None, project=None, **kw):
    super(Display1DWidget, self).__init__(parent)
    if self._appBase.ui.mainWindow is not None:
      self.mainWindow = self._appBase.ui.mainWindow
    else:
      self.mainWindow = self._appBase._mainWindow

    self.mainLayout = QtGui.QVBoxLayout()
    self.setLayout(self.mainLayout)


    display = self.mainWindow.createSpectrumDisplay(project.spectra[0])
    display.spectrumToolBar.hide()
    display.spectrumUtilToolBar.hide()
    display.module.hideTitleBar()
    self.mainLayout.addWidget(display.module)
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
__author__ = "$Author: luca $"
__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================
