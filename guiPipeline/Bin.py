
from PyQt4 import QtGui
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Label import Label
from collections import OrderedDict
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe, PipelineDropArea


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

class Bin(GuiPipe):
  preferredPipe = False

  def __init__(self, application, parent=None, name=None, params=None, **kw):
    super(Bin, self)
    GuiPipe.__init__(self, name=name, )
    self.application = application
    self.project = self.application.project
    self.spectra = [spectrum.pid for spectrum in self.project.spectra]

    self._setMainLayout()
    self._createWidgets()
    self.params = params
    if self.params is not None:
      self._setParams()
    if parent is not None:
      self.pipelineModule = parent

  def pipeName(self):
    return 'Bin'

  def runMethod(self):
    print('Running ',  self.name())

  def applicationsSpecific(self):
    return ['AnalysisMetabolomics']

  def _setMainLayout(self):
    self.mainFrame = QtGui.QFrame()
    self.mainLayout = QtGui.QGridLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0, 0, 0)

  def _createWidgets(self):
    self.binWidthLabel = Label(self, 'Bin Width (ppm) ')
    self.binWidth = DoubleSpinbox(self)
    self.mainLayout.addWidget(self.binWidthLabel, 0, 0)
    self.mainLayout.addWidget(self.binWidth, 0, 1)

  def getWidgetsParams(self):
    binWidth = self.binWidth.value()
    params = OrderedDict([
                          ('binWidth', binWidth),
                          ])
    self.params = params
    return params

  def _setParams(self):
    for widgetName, value in self.params.items():
      try:
        widget = getattr(self, str(widgetName))
        if widget.__class__.__name__ in WidgetSetters.keys():
          setWidget = getattr(widget, WidgetSetters[widget.__class__.__name__])
          setWidget(value)
        else:
          print('Value not set for %s in %s. Insert it on the "WidgetSetters" dictionary ' %(widget, self.name()))
      except:
        print('Impossible to restore %s value for %s. Check paramas dictionary in getWidgetParams' %(widgetName, self.name()))
