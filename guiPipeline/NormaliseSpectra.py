
from PyQt4 import QtGui
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from collections import OrderedDict
from ccpn.ui.gui.widgets.PipelineWidgets import PipelineBox, PipelineDropArea

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


class NormaliseSpectra(PipelineBox):
  def __init__(self, parent=None, name=None, params=None, project=None, **kw):

    super(NormaliseSpectra, self)
    PipelineBox.__init__(self,name=name,)

    if parent is not None:
      self.pipelineModule = parent

    self.project = project
    self.spectra = [spectrum.pid for spectrum in self.project.spectra]

    self._setMainLayout()
    self._createWidgets()

    self.lenSpectra = len(self.spectra)
    self.params = params
    if self.params is not None:
      self._setParams()


  def methodName(self):
    return 'Normalise Spectra'

  def runMethod(self):
    print('Running ',  self.name())

  def applicationsSpecific(self):
    return ['AnalysisMetabolomics']

  def _setMainLayout(self):
    self.mainFrame = QtGui.QFrame()
    self.mainLayout = QtGui.QGridLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0,0,0,0)

  def _createWidgets(self):
    self.selectMethodLabel = Label(self, 'Select Method')

    self.methodPulldownList = PulldownList(self)
    methods = ['Reference Peak',
               'Total Area',
               'PQN']
    self.methodPulldownList.setData(methods)

    self.mainLayout.addWidget(self.selectMethodLabel,0,0)
    self.mainLayout.addWidget(self.methodPulldownList, 0,1)

  def getWidgetsParams(self):
    methodPulldownList = self.methodPulldownList.currentText()

    params = OrderedDict([
                           ('methodPulldownList', methodPulldownList),
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
