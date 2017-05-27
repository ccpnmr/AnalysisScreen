
from PyQt4 import QtGui
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.PulldownList import PulldownList
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

class AlignSpectra(GuiPipe):

  preferredPipe = True

  def __init__(self, parent=None, project=None, name=None, params=None, **kw):
    super(AlignSpectra, self)
    GuiPipe.__init__(self, parent, name )

    self.parent = parent
    #   self.parent = parent
    self.project = None
    if project is not None:
      self.project = project

    self._setMainLayout()
    self._createWidgets()
    self.params = params
    if self.params is not None:
      self._setParams()

  def pipeName(self):
    return 'Align Spectra'

  def applicationsSpecific(self):
    return ['AnalysisScreen']

  @property
  def _inputData(self):
    if self.parent is not None:
      return list(self.parent._inputData)
    else:
      return []

  def runMethod(self):
    from ccpn.AnalysisScreen.lib.spectralProcessing.align import alignment
    if self.project is not None:
      referenceSpectrum = self.spectrumPulldown.currentObject()
      spectra = [spectrum for spectrum in self._inputData if spectrum != referenceSpectrum]
      if referenceSpectrum is not None:
        print(referenceSpectrum)
        print(spectra)
        if spectra:
          alignment._alignSpectra(referenceSpectrum, spectra)
          print('Running ',  self.name())

  def _setMainLayout(self):
    self.mainFrame = QtGui.QFrame()
    self.mainLayout = QtGui.QGridLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0, 0, 0)

  def _createWidgets(self):
    self.spectrumLabel = Label(self, 'Reference Spectrum')
    self.spectrumPulldown = PulldownList(self,)
    if self._inputData:
      self.spectrumPulldown.setData(texts=[sp.pid for sp in self._inputData],objects=self._inputData)

    self.mainLayout.addWidget(self.spectrumLabel, 0, 0)
    self.mainLayout.addWidget(self.spectrumPulldown, 0, 1)

  def getWidgetsParams(self):
    spectrumPulldown = self.spectrumPulldown.currentText()

    params = OrderedDict([
                          ('spectrumPulldown', spectrumPulldown),
                          ])
    self.params = params
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
