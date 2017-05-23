from PyQt4 import QtGui
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.PipelineWidgets import PipelineBox, PipelineDropArea
from collections import OrderedDict

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

class BaselineCorrection(PipelineBox):

  preferredMethod = True

  def __init__(self, parent=None, project=None, name=None, params=None, **kw):
    super(BaselineCorrection, self)
    PipelineBox.__init__(self, name=name,)
    self.parent = parent
    print(parent)
    self.project = None
    if project is not None:
      self.project = project

    self._setMainLayout()
    self._createWidgets()
    self.params = params
    if self.params is not None:
      self._setParams()

  def methodName(self):
    return 'Baseline Correction'

  def applicationsSpecific(self):
    return ['AnalysisScreen']

  def _baselineCorrection(self, spectra):
    correctedSpectra = []
    for sp in spectra:
      from ccpn.AnalysisScreen.lib.spectralProcessing.baselineCorrection import CWBC
      x = sp.positions
      y = sp.intensities
      newX, newy = CWBC.baselineCorrection(x, y, flatten=True)
      sp._positions = newX
      sp._intensities = newy
      correctedSpectra.append(sp)
    return correctedSpectra

  def runMethod(self):

    print('Running ',  self.name())
    print(self._getInputData())
    # if self.project is not None:
    #   correctedSpectra = self._baselineCorrection(self.project.spectra)
    print('Done ', self.name())

  def _getInputData(self):
    if self.parent is not None:
      return list(self.parent._inputData)
    else:
      return []

  def _setMainLayout(self):
    self.mainFrame = Frame(None, setLayout=False)
    self.mainLayout = QtGui.QGridLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0, 0, 0)

  def _createWidgets(self):
    self.spectrumLabel = Label(self, 'Baseline Correction',)


    self.mainLayout.addWidget(self.spectrumLabel, 0, 0)

  def getWidgetsParams(self):

    # spectrumPulldown = self.spectrumPulldown.currentText()
    #
    # params = OrderedDict([
    #                       ('spectrumPulldown', spectrumPulldown),
    #                       ])
    # self.params = params
    return self.params


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
