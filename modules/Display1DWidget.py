__author__ = 'luca'

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
