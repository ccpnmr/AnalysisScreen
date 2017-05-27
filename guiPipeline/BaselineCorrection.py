from PyQt4 import QtGui
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe, PipelineDropArea
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

class BaselineCorrection(GuiPipe):

  preferredPipe = True

  def __init__(self, parent=None, project=None, name=None, params=None, **kw):
    super(BaselineCorrection, self)
    GuiPipe.__init__(self, name=name, )
    self.parent = parent
    self.project = None
    if project is not None:
      self.project = project

    self._setMainLayout()
    self._createWidgets()
    self.params = params
    if self.params is not None:
      self._setParams()

  def pipeName(self):
    return 'Baseline Correction'

  def applicationsSpecific(self):
    return ['AnalysisScreen']

  @property
  def _inputData(self):
    if self.parent is not None:
      return list(self.parent._inputData)
    else:
      return []

  def _baselineCorrection(self, spectra, flatten=False, ratio=2):
    correctedSpectra = []
    for sp in spectra:
      from ccpn.AnalysisScreen.lib.spectralProcessing.baselineCorrection import CWBC
      x = sp.positions
      y = sp.intensities
      newX, newy = CWBC.baselineCorrection(x, y, flatten=flatten, ratio=ratio )
      sp._positions = newX
      sp._intensities = newy
      correctedSpectra.append(sp)
    return correctedSpectra

  def runMethod(self):
    removeNoise = self.getWidgetsParams()['flattenCheckBox']

    if self.project is not None:
      if len(self._inputData)>0:
        print('Running ',  self.name() ,' on ', self._inputData)
        correctedSpectra = self._baselineCorrection(self._inputData, flatten=removeNoise)
        print('Done ', self.name())
      print('No data. Drag and drop SP or SG on the settings inputData box')



  def _setMainLayout(self):
    self.mainFrame = Frame(None, setLayout=False)
    self.mainLayout = QtGui.QGridLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0, 0, 0)

  def _createWidgets(self):
    self.spectrumLabel = Label(self, 'Baseline Correction',)
    self.flattenCheckBox = CheckBox(self, text='Remove Noise')

    self.mainLayout.addWidget(self.spectrumLabel, 0, 0)
    self.mainLayout.addWidget(self.flattenCheckBox, 0, 1)


  def getWidgetsParams(self):

    flattenCheckBox = self.flattenCheckBox.get()

    params = OrderedDict([
                          ('flattenCheckBox', flattenCheckBox),
                          ])
    self.params = params
    print(self.params)
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
