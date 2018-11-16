#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license",
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license",
                 "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:25 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtGui, QtWidgets
from ccpn.AnalysisScreen.gui.modules.MixtureAnalysis import MixtureAnalysis
from ccpn.AnalysisScreen.gui.modules.MixtureOptimisation import SimulatedAnnealingWidgets
from ccpn.ui.gui.popups.PickPeaks1DPopup import ExcludeRegions

from ccpn.AnalysisScreen.lib.MixturesGeneration import _initialiseMixtures
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.widgets.Slider import SliderSpinBox
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.Button import Button
from collections import OrderedDict
from ccpn.ui.gui.popups.Dialog import CcpnDialog


class MixtureGenerationPopup(CcpnDialog):

    def __init__(self, parent=None, mainWindow=None, title='Mixture Generation Setup', **kwds):
        CcpnDialog.__init__(self, parent, setLayout=False, windowTitle=title, **kwds)

        if mainWindow is None:  #This allows opening the popup for graphical tests
            self.project = None
            self.current = None

        else:
            self.mainWindow = mainWindow
            self.project = self.mainWindow.project
            self.moduleArea = self.mainWindow.moduleArea
            self.application = self.mainWindow.application
            self.generalPreferences = self.application.preferences.general
            self.colourScheme = self.generalPreferences.colourScheme
            self.current = self.application.current

        self.settingIcon = Icon('icons/applications-system')
        self.excludedRegionsWidgets = ExcludeRegions(self)
        self.simulatedAnnealingParams = [OrderedDict([('initialTemp', 100), ('finalTemp', 1), ('max steps', 10),
                                                      ('temp constant', 50), ('cooling method', 'Linear'), ('iteration', 1)])]

        self._setMainLayout()
        self._setTabs()

        self._setcalculateButtons()
        self._addWidgetsToMainLayout()

        self._createWidgetsGeneralTab()
        self._createWidgetsTabPickPeaksSetup()
        self._populatePullDownSelection()
        self._setPerformButtonStatus()

    def _setMainLayout(self):
        self.mainLayout = QtWidgets.QGridLayout()
        self.setLayout(self.mainLayout)
        self.resize(600, 500)

    def _setTabs(self):
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabGeneralSetup = Frame(self, setLayout=False)
        self.tabGeneralSetupLayout = QtWidgets.QGridLayout()
        self.tabGeneralSetup.setLayout(self.tabGeneralSetupLayout)

        self.tabPickPeaksSetup = Frame(self, setLayout=False)
        self.tabPickPeaksSetupLayout = QtWidgets.QGridLayout()
        self.tabPickPeaksSetup.setLayout(self.tabPickPeaksSetupLayout)

        self.tabWidget.addTab(self.tabGeneralSetup, 'General Setup')
        self.tabWidget.addTab(self.tabPickPeaksSetup, 'Pick Peaks Setup')

    def _setcalculateButtons(self):
        self.calculateButtons = ButtonList(self,
                                           texts=['Cancel', 'Perform'],
                                           callbacks=[self.reject, self._genereteMixture],
                                           tipTexts=[None, None],
                                           direction='h', hAlign='c')

    def _addWidgetsToMainLayout(self):
        self.mainLayout.addWidget(self.tabWidget, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.calculateButtons, 7, 1)

    def _createWidgetsGeneralTab(self):

        methods = ['Simulated Annealing']
        mode = ['Select number of Mixtures', 'Select number of components']

        #
        self.calculationMethodLabel = Label(None, 'Calculation method')
        self.calculationMethod = RadioButtons(None, texts=methods,
                                              selectedInd=0,
                                              callback=self._showSAoptionWidgets,
                                              direction='h',
                                              hAlign='c',
                                              tipTexts=None)
        # #
        self.saSettingsLabel = Label(None, 'SA settings')
        self.saSettingsButton = Button(None, text='', callback=self._showSAsettings, icon=self.settingIcon)

        self.saSettingsButton.setFixedSize(30, 30)

        #
        self.modeLabel = Label(self, text='Select mode')
        self.modeRadioButtons = RadioButtons(None, texts=mode,
                                             selectedInd=1,
                                             callback=self._modeSelection,
                                             direction='v',
                                             hAlign='c',
                                             tipTexts=None)
        #
        self.numberLabel = Label(self, text='Select number')
        self.numberSlider = SliderSpinBox(None, value=2, startVal=2, endVal=100, step=1, bigStep=5,
                                          hAlign='c')

        #
        self.distanceLabel = Label(None, text="Minimal distance between peaks")
        self.ppmDistance = DoubleSpinbox(None)
        self.ppmDistance.setRange(0.00, 0.20)
        self.ppmDistance.setValue(0.01)
        self.ppmDistance.setSingleStep(0.01)
        self.ppmDistance.setSuffix(" ppm")
        #
        # #
        self.selectSpectraLabel = Label(None, text="Select SpectrumGroup")
        self.selectSpectraPullDown = PulldownList(None)

        #
        # self.replaceLabel = Label(self, text="Replace current mixtures")
        # self.replaceRadioButtons = RadioButtons(self,
        #                                           texts=['Yes', 'No'],
        #                                           selectedInd=0,
        #                                           callback=None,
        #                                           direction='v',
        #                                           tipTexts=None)

        widgetsGeneralTab = (
            self.calculationMethodLabel, self.calculationMethod,
            self.saSettingsLabel, self.saSettingsButton,
            self.modeLabel, self.modeRadioButtons,
            self.numberLabel, self.numberSlider,
            self.distanceLabel, self.ppmDistance,
            self.selectSpectraLabel, self.selectSpectraPullDown,
            # self.replaceLabel, self.replaceRadioButtons
            )

        self._addWidgetsToTabLayout(widgetsGeneralTab, self.tabGeneralSetupLayout)

    def _createWidgetsTabPickPeaksSetup(self):

        # 1
        self.pickPeaksLabel = Label(self, text="Peak Picking")
        self.pickPeaksRadioButtons = RadioButtons(self,
                                                  texts=['Automatic', 'Already picked'],
                                                  selectedInd=0,
                                                  callback=self._pickPeakCallBack,
                                                  tipTexts=None,
                                                  direction='v',
                                                  )

        #2
        self.noiseLabel = Label(self, text="Select noise level")
        self.noiseLevelRadioButtons = RadioButtons(self,
                                                   texts=['Estimated', 'Manual'],
                                                   selectedInd=0,
                                                   callback=self._noiseLevelCallBack,
                                                   tipTexts=None,
                                                   direction='v',
                                                   )
        # 3
        self.noiseThresholdLabel = Label(self, text="Select noise level threshold")
        self.noiseLevelSpinbox = DoubleSpinbox(self)
        self.noiseLevelSpinbox.setMaximum(100000.00)

        self.noiseLevelFactorLabel = Label(self, text='Noise Level Factor')
        self.noiseLevelFactorSpinbox = DoubleSpinbox(self, value=10.0, min=0.01, step=0.1)

        # 4
        self.filterLabel = Label(self, text="Select filter size")
        self.filterSpinbox = Spinbox(self)
        self.filterSpinbox.setValue(8)
        self.filterSpinboxWidth = self.filterSpinbox.frameGeometry().width()

        # 5
        modes = ['wrap', 'reflect', 'constant', 'nearest', 'mirror']
        self.maximumFilterMode = Label(self, text="Select Maximum Filter Mode")
        self.maximumFilterModePulldownList = PulldownList(self, texts=modes)
        self.maximumFilterModePulldownList.setMinimumWidth(50)

        widgetsGeneralTab = (self.pickPeaksLabel, self.pickPeaksRadioButtons,
                             self.noiseLabel, self.noiseLevelRadioButtons,
                             self.noiseThresholdLabel, self.noiseLevelSpinbox,
                             self.noiseLevelFactorLabel, self.noiseLevelFactorSpinbox,
                             self.filterLabel, self.filterSpinbox,
                             self.maximumFilterMode, self.maximumFilterModePulldownList
                             )

        self._addWidgetsToTabLayout(widgetsGeneralTab, self.tabPickPeaksSetupLayout)
        self.tabPickPeaksSetupLayout.addWidget(self.excludedRegionsWidgets, 10, 0, 11, 2)
        self._hideWidgets([self.noiseThresholdLabel, self.noiseLevelSpinbox])

    def _addWidgetsToTabLayout(self, widgets, layout):
        count = int(len(widgets) / 2)
        self.positions = [[i + 1, j] for i in range(count) for j in range(2)]
        for position, widget in zip(self.positions, widgets):
            i, j = position
            layout.addWidget(widget, i, j)

    def _showSAoptionWidgets(self):

        if self.calculationMethod.get() == 'Simulated Annealing':
            self.saSettingsLabel.show()
            self.saSettingsButton.show()
        else:
            self.saSettingsLabel.hide()
            self.saSettingsButton.hide()

    def _modeSelection(self):
        '''   '''
        selected = self.modeRadioButtons.get()
        callbacks = (self._changeLabelNumberMixtures, self._showNComponents)
        for selection, callback in zip(self.modeRadioButtons.texts, callbacks):
            if selected == str(selection):
                callback()

    def _pickPeakCallBack(self, ):
        '''   '''
        selected = self.pickPeaksRadioButtons.get()
        widgets = (self.noiseLabel, self.noiseLevelRadioButtons,
                   self.noiseThresholdLabel, self.noiseLevelSpinbox,
                   self.filterLabel, self.filterSpinbox,
                   self.maximumFilterMode, self.maximumFilterModePulldownList,
                   self.excludedRegionsWidgets, self.noiseLevelFactorLabel,
                   self.noiseLevelFactorSpinbox)

        if selected == 'Automatic':
            self.noiseLevelRadioButtons.radioButtons[1].setChecked(True)
            self._showWidgets(widgets)
        else:
            self._hideWidgets(widgets)

    def _noiseLevelCallBack(self):
        '''   '''
        selected = self.noiseLevelRadioButtons.get()
        if selected == 'Estimated':
            self._hideWidgets([self.noiseLevelSpinbox, self.noiseThresholdLabel])
        else:
            self._showWidgets([self.noiseLevelSpinbox, self.noiseThresholdLabel])

    def _changeLabelNumberMixtures(self):
        '''   '''
        self.numberLabel.setText('Select N of Mixtures')

    def _showNComponents(self):
        '''   '''
        self.numberLabel.setText('Select N of Components')

    def _hideWidgets(self, widgets: []):
        for widget in widgets:
            widget.hide()

    def _showWidgets(self, widgets: []):
        for widget in widgets:
            widget.show()

    def _populatePullDownSelection(self):
        '''   '''
        self.dataPullDown = ['Select An Option']
        if self.project is not None:
            if len(self.project.spectrumGroups) > 0:
                self.dataPullDown.append('All Spectra')
                for spectrumGroup in self.project.spectrumGroups:
                    self.dataPullDown.append(spectrumGroup.pid)
            self.selectSpectraPullDown.setData(self.dataPullDown)
            if 'SG:H' in self.dataPullDown:
                self.selectSpectraPullDown.select('SG:H')

            self.selectSpectraPullDown.activated[str].connect(self._setPerformButtonStatus)

    def _getPullDownSelectionSpectra(self):
        '''   '''
        selected = self.selectSpectraPullDown.getText()
        if selected == 'All Spectra':
            spectra = self.project.spectra
            return spectra
        if selected == 'Select An Option':
            return []
        else:
            spectra = self.project.getByPid(selected).spectra
            return spectra

    def _deleteMixtures(self):
        mixtures = MixtureAnalysis._getVirtualSamples(self)
        if len(mixtures) > 0:
            for mixture in mixtures:
                mixture.delete()
        if 'MIXTURE ANALYSIS' in self.moduleArea.findAll()[1]:
            self.moduleArea.modules['MIXTURE ANALYSIS'].close()

    def _showSAsettings(self):
        self.saPopup = SAsettingPopup(parent=self, project=self.project, params=self.simulatedAnnealingParams[-1])
        self.saPopup.exec_()
        self.saPopup.raise_()

    def _getAllParameters(self):
        calculationMethod = str(self.calculationMethod.get())
        simulatedAnnealingParm = self.simulatedAnnealingParams[-1]
        mode = str(self.modeRadioButtons.get())
        number = self.numberSlider.getValue()
        minimalDistance = self.ppmDistance.value()
        spectra = self._getPullDownSelectionSpectra()
        # replace = str(self.replaceRadioButtons.get())
        peakPicking = str(self.pickPeaksRadioButtons.get())
        noiseLevel = str(self.noiseLevelRadioButtons.get())
        threshold = self.noiseLevelSpinbox.value()
        filter = self.filterSpinbox.value()
        filterMode = self.maximumFilterModePulldownList.getText()
        ignoredRegions = self.excludedRegionsWidgets._getExcludedRegions()
        factor = self.noiseLevelFactorSpinbox.value()

        params = OrderedDict((
            ('calculationMethod', calculationMethod),
            ('simulatedAnnealingParm', simulatedAnnealingParm),
            ('mode', mode),
            ('number', number),
            ('minimalDistance', minimalDistance),
            ('spectra', spectra),
            # ('replace', replace),
            ('peakPicking', peakPicking),
            ('noiseLevel', noiseLevel),
            ('threshold', threshold),
            ('factor', factor),
            ('filter', filter),
            ('filterMode', filterMode),
            ('ignoredRegions', ignoredRegions)
            ))
        return params

    def _genereteMixture(self):
        '''This function gets all the setting given by the user and runs the mixture generation algorithms'''
        parameters = self._getAllParameters()
        _initialiseMixtures(parameters)
        self._openMixtureAnalysisModule()
        self.accept()

    def _setPerformButtonStatus(self):
        ''' Activetes the perform button if spectra are selected  '''
        selected = self.selectSpectraPullDown.getText()
        if selected == 'Select An Option':
            self.calculateButtons.buttons[1].setEnabled(False)
        else:
            self.calculateButtons.buttons[1].setEnabled(True)

    def _openMixtureAnalysisModule(self):
        '''   '''
        mixtureAnalysis = MixtureAnalysis(minimalDistance=self.ppmDistance.value(), mainWindow=self.mainWindow)
        mixtureAnalysisModule = self.moduleArea.addModule(mixtureAnalysis, position='bottom')

        spectrumDisplay = self.mainWindow.createSpectrumDisplay(self.project.spectra[0])
        self.mainWindow.moduleArea.addModule(spectrumDisplay, position='top',
                                             relativeTo=self.mainWindow.moduleArea)
        spectrumDisplay.setWhatsThis('MixtureDisplay')

        self.moduleArea.moveModule(spectrumDisplay, position='top', neighbor=mixtureAnalysisModule)
        # self.moduleArea.guiWindow.deleteBlankDisplay()
        # self.project.strips[0].viewBox.autoRange()
        if self.current is not None:
            currentDisplayed = self.current.strip
            if currentDisplayed is not None:
                for spectrumView in currentDisplayed.spectrumViews:
                    if spectrumView is not None:
                        spectrumView.delete()


class SAsettingPopup(QtWidgets.QDialog):

    def __init__(self, parent=None, project=None, params=None, **kwds):
        super(SAsettingPopup, self).__init__(parent)
        self.project = project
        self._parent = parent

        i, f, s, k, c, it = list(params.values())
        self.simulatedAnnealingWidgets = SimulatedAnnealingWidgets(i, f, s, k, c, it)
        self._setMainLayout()
        self._setWidgets()
        self._addWidgetsToMainLayout()

    def _setMainLayout(self):
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Simulated Annealing Setup")
        self.resize(150, 300)

    def _setWidgets(self):
        self.okCancelButtons = ButtonList(self,
                                          texts=['Cancel', 'Ok'],
                                          callbacks=[self.reject, self._okButton],
                                          tipTexts=[None, None],
                                          direction='h', hAlign='r')

    def _addWidgetsToMainLayout(self):
        self.mainLayout.addWidget(self.simulatedAnnealingWidgets)
        self.mainLayout.addWidget(self.okCancelButtons)

    def _okButton(self):
        param = self.simulatedAnnealingWidgets._getParam()
        self._parent.simulatedAnnealingParams.append(param)
        self.accept()


if __name__ == '__main__':
    from ccpn.ui.gui.widgets.Application import TestApplication


    app = TestApplication()
    popup = MixtureGenerationPopup(mainWindow=None)
    popup.show()
    popup.raise_()
    app.start()
