
from PyQt4 import QtGui

from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.popups.PickPeaks1DPopup import ExcludeRegions
from collections import OrderedDict
import pyqtgraph as pg
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe, PipelineDropArea
from functools import partial
import copy

WidgetSetters = OrderedDict([
                            ('CheckBox',      'setChecked'),
                            ('PulldownList',  'set'       ),
                            ('LineEdit',      'setText'   ),
                            ('Label',         'setText'   ),
                            ('DoubleSpinbox', 'setValue'  ),
                            ('Spinbox',       'setValue'  ),
                            ('Slider',        'setValue'  ),
                            ('RadioButtons',  'setIndex'  ),
                            ('TextEditor',    'setText'   ),
                           ])


class ExcludeSignalFreeRegions(GuiPipe):
  preferredPipe = False

  def __init__(self, application, parent=None, name=None, params=None, **kw):
    super(ExcludeSignalFreeRegions, self)
    GuiPipe.__init__(self, name=name, )

    self.application = application
    self.project = self.application.project
    self.spectra = [spectrum.pid for spectrum in self.project.spectra]
    self._setMainLayout()
    self._createWidgets()
    if parent is not None:
      self.pipelineModule = parent
    self.params = params
    if self.params is not None:
      self._setParams()


  def pipeName(self):
    return 'Exclude Signal Free Regions'

  def applicationsSpecific(self):
    return [ 'AnalysisMetabolomics']

  def runMethod(self):
    print('Running ',  self.name())
    return self.excludeRegionsWidget._getExcludedRegions()

  def _setMainLayout(self):
    self.mainFrame = QtGui.QFrame()
    self.mainLayout = QtGui.QHBoxLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0, 0, 0)

  def _createWidgets(self):
    self.excludeRegionsWidget = ExcludeRegions(self)
    self.mainLayout.addWidget(self.excludeRegionsWidget)



  def getWidgetsParams(self):
    self.params = self.excludeRegionsWidget.getSolventsAndValues()

    return self.params


  def _setParams(self):
    originalSolvents = copy.deepcopy(self.excludeRegionsWidget.solvents)
    for solvent in sorted(self.params.keys()):
      try:
        self.excludeRegionsWidget.solvents = self.params
        self.excludeRegionsWidget._addRegions(solvent)
      except:
        pass

    self.excludeRegionsWidget.solvents = originalSolvents




