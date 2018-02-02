from collections import OrderedDict

from PyQt5 import QtGui, QtWidgets

from ccpn.AnalysisScreen.lib.MixturesGeneration import _getMixturesFromVirtualSamples, _createSamples
from ccpn.AnalysisScreen.lib.SimulatedAnnealing import  iterateAnnealing, showScoresPerMixture
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.Frame import Frame


class SimulatedAnnealingWidgets(Frame):
  def __init__(self, initialTemp=1000, finalTemp=1, stepTemp=1000, constantTemp=30, coolingMethod='Linear', iterations=3):
    Frame.__init__(self)

    self.mainLayout = QtWidgets.QGridLayout()
    self.setLayout(self.mainLayout)
    self.coolingMethod = coolingMethod


  # def _createWidgets(self):
    #0  initial Temperature
    self.initialTempLabel = Label(self, 'Initial Temperature')
    self.initialTempSpinbox = Spinbox(self)
    self.initialTempSpinbox.setMaximum(100000)
    self.initialTempSpinbox.setValue(initialTemp)


    # 1  final Temperature
    self.finalTempLabel = Label(self, 'Final Temperature')
    self.finalTempSpinbox = Spinbox(self)
    self.finalTempSpinbox.setMaximum(100000)
    self.finalTempSpinbox.setValue(finalTemp)


    # 2  Step Temperature
    self.stepTempLabel = Label(self, 'Max Steps')
    self.stepTempSpinbox = Spinbox(self)
    self.stepTempSpinbox.setMaximum(100000)
    self.stepTempSpinbox.setValue(stepTemp)


    # 3  constant Temperature
    self.constantTempLabel = Label(self, 'Probability Constant')
    self.constantTempSpinbox = Spinbox(self)
    self.constantTempSpinbox.setMaximum(100000)
    self.constantTempSpinbox.setValue(constantTemp)




    # 4  cooling Method
    self.coolingLabel = Label(self, 'Cooling method')
    self.coolingMethodRadiobutton = RadioButtons(self,
                                               texts=['Exponential', 'Linear'],
                                               selectedInd=1,
                                               callback=None,
                                               tipTexts=None)

    # 5  constant Temperature
    self.iterationLabel = Label(self, 'Iteration')
    self.iterationSpinbox = Spinbox(self)
    self.iterationSpinbox.setMaximum(100000)
    self.iterationSpinbox.setValue(iterations)

    if self.coolingMethod == 'Linear':
      self.coolingMethodRadiobutton.radioButtons[1].setChecked(True)
    else:
      self.coolingMethodRadiobutton.radioButtons[0].setChecked(True)

    self._addWidgetsToLayout()

  def _addWidgetsToLayout(self):
    self.widgets = [self.initialTempLabel,self.initialTempSpinbox,
                    self.finalTempLabel,self.finalTempSpinbox,
                    self.stepTempLabel,self.stepTempSpinbox,
                    self.constantTempLabel,self.constantTempSpinbox,
                    self.coolingLabel,self.coolingMethodRadiobutton,
                    self.iterationLabel,self.iterationSpinbox]

    count = int(len(self.widgets) / 2)
    self.positions = [[i + 1, j] for i in range(count) for j in range(2)]
    for position, widget in zip(self.positions, self.widgets):
      i, j = position
      self.mainLayout.addWidget(widget, i, j)

  def _getParam(self):

    param = OrderedDict((
                        ('initialTemp', self.initialTempSpinbox.value()),
                        ('finalTemp', self.finalTempSpinbox.value()),
                        ('max steps', self.stepTempSpinbox.value()),
                        ('temp constant', self.constantTempSpinbox.value()),
                        ('cooling method', str(self.coolingMethodRadiobutton.get())),
                        ('iteration' , self.iterationSpinbox.value())
                        ))
    return param

class MixtureOptimisation(CcpnModule):

  '''Creates a module to analyse the mixtures'''

  def __init__(self, mainWindow, name='Mixture Optimisation', virtualSamples=None, mixtureAnalysisModule=None, minimalDistance=0.01,):
    super(MixtureOptimisation, self)
    CcpnModule.__init__(self, mainWindow=mainWindow,  name=name)

    self.mainWindow = mainWindow
    self.project = mainWindow.project
    self.application = self.mainWindow.application
    self.mixtureAnalysisModule = mixtureAnalysisModule
    self.minimalDistance = minimalDistance

    self.virtualSamples = virtualSamples

    ######## ======== Set Main Layout ====== ########
    self.mainFrame = Frame()
    self.mainLayout = QtWidgets.QVBoxLayout()
    self.mainFrame.setLayout(self.mainLayout)
    self.layout.addWidget(self.mainFrame, 0, 0)

    ######## ======== Set Secondary Layout ====== ########
    self.settingFrameLayout = QtWidgets.QHBoxLayout()
    self.buttonsFrameLayout = QtWidgets.QHBoxLayout()
    self.mainLayout.addLayout(self.settingFrameLayout)
    self.mainLayout.addLayout(self.buttonsFrameLayout)

    ######## ======== Set Tabs  ====== ########
    self.tabWidget = QtWidgets.QTabWidget()
    self.settingFrameLayout.addWidget(self.tabWidget)
    self.scoringListWidget = ListWidget(self, contextMenu=False)
    self.settingFrameLayout.addWidget(self.scoringListWidget)

    ######## ======== Set Buttons  ====== ########
    self.panelButtons = ButtonList(self, texts=[ 'Perform','Apply'],
                                   callbacks=[self._recalculateMixtures, self._applyNewMixtures],
                                   icons=[None, None],
                                   tipTexts=[ None, None],
                                   direction='H',
                                   hAlign= 'c')
    self.buttonsFrameLayout.addWidget(self.panelButtons)
    # self._disableButtons()

    ######## ======== Set 1 Tab  ====== ########
    self.tabWidget.addTab(SimulatedAnnealingWidgets(), 'SA settings')





  def _setTabOtherOptions(self):
    self.tab2Frame = Frame()
    self.tab2Layout = QtWidgets.QGridLayout()
    self.tab2Frame.setLayout(self.tab2Layout)
    self.tabWidget.addTab(self.tab2Frame, 'Others')

  def _setOtherOptionsWidgets(self):
    self.replaceMixtureLabel = Label(self, text="Replace Mixtures")
    self.replaceRadioButtons = RadioButtons(self,
                                            texts=['Yes', 'No'],
                                            selectedInd=0,
                                            callback=None,
                                            tipTexts=None)
    self.tab2Layout.addWidget(self.replaceMixtureLabel, 0,0)
    self.tab2Layout.addWidget(self.replaceRadioButtons, 0,1)

  def _disableButtons(self):
    for button in self.panelButtons.buttons:
      button.setEnabled(False)
      button.setStyleSheet("background-color:#868D9D; color: #000000")

  def _recalculateMixtures(self):
    simulatedAnnealing = SimulatedAnnealingWidgets()
    params = simulatedAnnealing._getParam()
    i, f, s, k, c, it = list(params.values())
    mixtures = _getMixturesFromVirtualSamples(self.virtualSamples)
    newMixtures = iterateAnnealing(mixtures, i, f, s, k, c, it, minDistance=self.minimalDistance)
    self.newMixtures = newMixtures
    self.showScoresOnListWidget(newMixtures)


  def _applyNewMixtures(self):
    self.deleteCurrentVirtualSamples(self.virtualSamples)
    _createSamples(self.project, self.newMixtures,self.minimalDistance)
    self.mixtureAnalysisModule.scoringTable.setObjects(self.mixtureAnalysisModule._getVirtualSamples())
    self.close()


  def deleteCurrentVirtualSamples(self, virtualSamples):
    for sample in virtualSamples:
      sample.delete()

  def showScoresOnListWidget(self, newMixtures):
    scores = showScoresPerMixture(newMixtures, self.minimalDistance)
    for score in scores:
      self.scoringListWidget.addItem(score)
