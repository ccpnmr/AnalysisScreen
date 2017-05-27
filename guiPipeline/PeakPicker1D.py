
from collections import OrderedDict
from PyQt4 import QtGui , QtCore
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.PipelineWidgets import GuiPipe
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.widgets.Label import Label

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

class PeakPicker1D(GuiPipe):
  preferredPipe = True

  def __init__(self, parent=None,project=None, name=None, params=None, **kw):
    super(PeakPicker1D, self)
    GuiPipe.__init__(self, name=name, )
    self.parent = parent
    self.project = project
    self._setMainLayout()
    self._createWidgets()
    self.params = params
    if self.params is not None:
      self._setParams()

    if parent is not None:
      self.pipelineModule = parent

  def pipeName(self):
    return 'Peak picker 1D'

  def applicationsSpecific(self):
    return ['AnalysisScreen', 'AnalysisMetabolomics']

  @property
  def _inputData(self):
    if self.parent is not None:
      return list(self.parent._inputData)
    else:
      return []

  def _setMainLayout(self):
    self.mainFrame = Frame(None, setLayout = False)
    self.mainLayout = QtGui.QGridLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0, 0, 0)

  def _createWidgets(self):

    self.pickNegativeLabel = Label(self, text='Pick negative peaks')
    self.pickNegativeCheckBox = CheckBox(self, text='', checked=True)

    self.noiseLevelLabel = Label(self, text='Noise Level Threshold')
    self.noiseLevelRadioButtons = RadioButtons(self,
                                               texts=['Estimated', 'Manual'],
                                               selectedInd=0,
                                               callback=self._noiseLevelCallBack,
                                               tipTexts=None)
    self.noiseLevelSpinbox = DoubleSpinbox(self)
    self.noiseLevelSpinbox.hide()
    self.noiseLevelSpinbox.setValue(10000)
    self.noiseLevelSpinbox.setMaximum(10000000)

    self.maximumFilterSize = Label(self, text="Select Maximum Filter Size")
    self.maximumFilterSizeSpinbox = Spinbox(self)
    self.maximumFilterSizeSpinbox.setValue(5)
    self.maximumFilterSizeSpinbox.setMaximum(15)

    modes = ['wrap', 'reflect', 'constant', 'nearest', 'mirror']
    self.maximumFilterMode = Label(self, text="Select Maximum Filter Mode")
    self.maximumFilterModePulldownList = PulldownList(self, texts=modes)

    self.mainLayout.addWidget(self.pickNegativeLabel, 0,0)
    self.mainLayout.addWidget(self.pickNegativeCheckBox, 0,1)

    self.mainLayout.addWidget(self.noiseLevelLabel, 1,0)
    self.mainLayout.addWidget(self.noiseLevelRadioButtons, 1,1)

    self.mainLayout.addWidget(self.noiseLevelSpinbox, 2,1)

    self.mainLayout.addWidget(self.maximumFilterSize, 3,0)
    self.mainLayout.addWidget(self.maximumFilterSizeSpinbox, 3,1)

    self.mainLayout.addWidget(self.maximumFilterMode, 4,0)
    self.mainLayout.addWidget(self.maximumFilterModePulldownList, 4,1)

  def _noiseLevelCallBack(self):
    selected = self.noiseLevelRadioButtons.get()
    if selected == 'Estimated':
      self.noiseLevelSpinbox.hide()
    else:
      self.noiseLevelSpinbox.show()

  def getWidgetsParams(self):
    self.params = OrderedDict([
                          ('pickNegativeCheckBox', self.pickNegativeCheckBox.get()),
                          ('maximumFilterSizeSpinbox' , self.maximumFilterSizeSpinbox.value()),
                          ('noiseLevelSpinbox',         self.noiseLevelSpinbox.value()),
                          ('maximumFilterModePulldownList', self.maximumFilterModePulldownList.getText())
                          ])
    return self.params


  def runMethod(self):
    print('Running ',  self.pipeName())
    if self._inputData:
      self._pickPeaks(self._inputData)
    else:
      print('No data. Drag and drop SP or SG on the settings inputData box')


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

  def _pickPeaks(self, spectra):
    negativePeaks = self.pickNegativeCheckBox.get()
    # ignoredRegions = self._getIgnoredRegions()
    #@ ignoredRegions = ignoredRegions
    size = self.getWidgetsParams()['maximumFilterSizeSpinbox']
    mode = self.getWidgetsParams()['maximumFilterModePulldownList']
    # noiseThreshold = self.getWidgetsParams()['noiseLevelSpinbox']

    for spectrum in spectra:
      spectrum.peakLists[0].pickPeaks1dFiltered(size=size, mode=mode,
                                                # noiseThreshold=noiseThreshold,
                                                negativePeaks=negativePeaks)

  def _getIgnoredRegions(self):
    # FIXME
    ignoredRegions = []
    if self.pipelineModule is not None:
      currentPipeline = OrderedDict(self.pipelineModule.currentRunningPipeline)
      for box, value in currentPipeline.items():
        if box.pipeName() == 'Exclude Signal Free Regions':
          ignoredRegions += value
      if len(ignoredRegions)>0:
        return ignoredRegions