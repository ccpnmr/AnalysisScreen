#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2019"
__credits__ = ("Ed Brooksbank, Luca Mureddu, Timothy J Ragan & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license")
__reference__ = ("Skinner, S.P., Fogh, R.H., Boucher, W., Ragan, T.J., Mureddu, L.G., & Vuister, G.W.",
                 "CcpNmr AnalysisAssign: a flexible platform for integrated NMR analysis",
                 "J.Biomol.Nmr (2016), 66, 111-124, http://doi.org/10.1007/s10858-016-0060-y")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: CCPN $"
__dateModified__ = "$dateModified: 2017-07-07 16:32:24 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.b4 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from functools import partial

from PyQt5 import QtCore, QtGui, QtWidgets

from ccpn.AnalysisScreen.lib.MixturesGeneration import _getCompounds, _createSamples
from ccpn.AnalysisScreen.lib.SimulatedAnnealing import calculateOverlapCount, scoreMixture
from ccpn.AnalysisScreen.gui.modules.MixtureOptimisation import MixtureOptimisation
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.Button import Button

from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.CompoundView import CompoundView
from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.LineEdit import LineEdit
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.widgets.Menu import Menu
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Table import ObjectTable, Column


green = QtGui.QColor('Green')
red = QtGui.QColor('Red')
yellow = QtGui.QColor('yellow')
DefaultMinimalDistance = 0.01  #ppm


class MixtureAnalysis(CcpnModule):
    '''Creates a module to analyse the mixtures'''

    includeSettingsWidget = False
    maxSettingsState = 2
    className = 'MixtureAnalysis'

    def __init__(self, mainWindow, name='Mixture Analysis', minimalDistance=None):
        super(MixtureAnalysis, self)

        #This allows opening the popup for graphical tests
        self.project = None
        CcpnModule.__init__(self, mainWindow=mainWindow, name=name)
        if mainWindow is not None:
            self.mainWindow = mainWindow
            self.project = self.mainWindow.project
            self.application = self.mainWindow.application
            self.moduleArea = self.mainWindow.moduleArea
            self.preferences = self.application.preferences
            self.current = self.application.current

        self.listOfSample = []

        if minimalDistance is None:
            minimalDistance = DefaultMinimalDistance
        self.minimalDistance = minimalDistance

        ######## ======== Icons ====== ########
        self.settingIcon = Icon('icons/configure')
        self.exportIcon = Icon('icons/export')

        ######## ======== Set Main Layout ====== ########
        self.mainFrame = Frame(self.mainWidget, setLayout=False)
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainFrame.setLayout(self.mainLayout)
        self.mainWidget.getLayout().addWidget(self.mainFrame, 0, 0)

        ######## ======== Set Secondary Layout ====== ########
        self.settingFrameLayout = QtWidgets.QHBoxLayout()
        self.analysisFrameLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.settingFrameLayout)
        self.mainLayout.addLayout(self.analysisFrameLayout)

        ######## ======== Create widgets ====== ########
        self._createSettingGroup()
        self._scoringTable()

        ######## ======== Set Tabs  ====== ########
        self.tabWidget = QtWidgets.QTabWidget()
        self.analysisFrameLayout.addWidget(self.tabWidget)

        ######## ======== Create 1thTab with peak Table and Molecule view  ====== ########
        self.tabPeaksMolecule = Frame(None, setLayout=False)
        self.tabPeaksMoleculeLayout = QtWidgets.QGridLayout()
        self.tabPeaksMolecule.setLayout(self.tabPeaksMoleculeLayout)
        self.tabWidget.addTab(self.tabPeaksMolecule, 'Components peaks')
        self.toolBarComponents = QtGui.QToolBar()
        self.tabPeaksMoleculeLayout.addWidget(self.toolBarComponents, 0, 0, 1, 0)

        ######## ========  Create 2ndTab with multiple Molecule view ====== ########
        self.tabMoleculeView = Frame(None, setLayout=False)
        self.tabMoleculeViewLayout = QtWidgets.QHBoxLayout()
        self.tabMoleculeView.setLayout(self.tabMoleculeViewLayout)
        self.tabWidget.addTab(self.tabMoleculeView, 'Components structure')
        self._tableComponentPeaks()

        ######## ========  Create 3thTab with Components Info ====== ########
        self.tabMoleculeInfo = Frame(None, setLayout=False)
        self.tabMoleculeInfoLayout = QtWidgets.QVBoxLayout()
        self.tabMoleculeInfo.setLayout(self.tabMoleculeInfoLayout)
        self.tabWidget.addTab(self.tabMoleculeInfo, 'Components Info')
        self._widgetsTabComponentsInfo()

        ######## ========  Create 4thTab Mixtures Management ====== ########
        self.tabMixturesManagement = Frame(None, setLayout=False)
        self.tabMixturesManagementLayout = QtWidgets.QGridLayout()
        self.tabMixturesManagement.setLayout(self.tabMixturesManagementLayout)
        self.tabWidget.addTab(self.tabMixturesManagement, 'Mixtures Management')
        self._mixtureManagementWidgets()

    def setMinimalDistanceForNewMixtures(self, value):
        self.minimalDistance = value

    def _getVirtualSamples(self):
        ''' Returns spectra mixtures (virtual samples) across all project sample '''
        self.virtualSamples = []
        if self.project is not None:
            if len(self.project.samples) > 0:
                for sample in self.project.samples:
                    if sample.isVirtual:
                        self.virtualSamples.append(sample)
                        if not hasattr(sample, 'overlaps'):
                            sample.overlaps = None
                        elif not hasattr(sample, 'score'):
                            sample.score = None
                    for sampleComponent in sample.sampleComponents:
                        if not hasattr(sampleComponent, 'score'):
                            sampleComponent.score = None
        return self.virtualSamples

    '''######## ======== Scoring and Selection Table ====== ########'''

    def _scoringTable(self):
        ''' Fills the first table on the module with the virtual sample information '''

        columns = [Column('Mixture Name', lambda sample: str(sample.pid)),
                   Column('N Components', lambda sample: str(len(sample.sampleComponents))),
                   Column('N Overlaps', lambda sample: str(sample.overlaps)),
                   Column('Score', lambda sample: str(sample.score)),
                   ]

        self.scoringTable = ObjectTable(self, columns, objects=[], selectionCallback=self._tableSelection)
        self.scoringTable.setFixedWidth(400)
        if len(self._getVirtualSamples()) > 0:
            self.scoringTable.setObjects(self._getVirtualSamples())
        self.analysisFrameLayout.addWidget(self.scoringTable)

    def _tableSelection(self, row: int = None, col: int = None, obj: object = None):
        ''' For each row of the scoring table all the module information are refreshed '''
        objRow = self.scoringTable.getCurrentObject()
        self._createButtons(objRow)
        self._displayMixture(objRow)
        self._displayMolecules(objRow)
        self._displayMixturesInfo(objRow)
        self._populatePullDownSelection()
        self._populateLeftListWidget()
        self.rightListWidget.clear()
        self._selectAnOptionState()

    ''' ######## ======== First Tab properties ====== ########   '''

    def _tableComponentPeaks(self, ):
        ''' This creates the peak table in the first tab'''
        self.peakListObjects = []

        columns = [Column('#', 'serial'),
                   Column('Position', lambda peak: '%.3f' % peak.position[0]),
                   Column('Height', lambda peak: peak.height)]

        self.peakTable = ObjectTable(self, columns, objects=[], selectionCallback=None, multiSelect=True)
        self.tabPeaksMoleculeLayout.addWidget(self.peakTable, 1, 0)

    # def _findSelectedPeaks(self, peaks:None):
    #   ''' this callback, registered with a notifier, allows to select a peak either on the table, compoundView or
    #   guiSpectrum display and highLight the respective peak/s or atom/s on compoundView, table, display '''
    #   # self.peakTable.clearSelection()
    #   selectedPeaks = []
    #   if self.project.strips:
    #     currentDisplayed = self.project.strips[0]
    #     if self.current.peaks:
    #       self.currentPeaks = self.current.peaks
    #       if self.peakTable.objects:
    #         for peak in self.currentPeaks:
    #           if peak in self.peakTable.objects:
    #             self.peakTable.setCurrentObject(peak)
    #             selectedPeaks.append(peak)
    #
    #   if selectedPeaks:
    #     print(selectedPeaks, 'selected peaks')
    #     self.peakTable.setCurrentObjects(selectedPeaks)
    #
    #     for atom, atomObject in self.compoundView.atomViews.items():
    #       if atom.name == 'H1':
    #         atomObject.select()

    def _createButtons(self, sample):
        ''' This creates buttons according with how many spectra are inside the mixture. '''
        self.toolBarComponents.clear()
        for sampleComponent in sample.sampleComponents:
            if sampleComponent.substance is not None:
                if len(sampleComponent.substance.referenceSpectra) > 0:
                    spectrum = sampleComponent.substance.referenceSpectra[0]
                else:
                    spectrum = self.project.getByPid('SP:' + str(sampleComponent.substance.name))
                if spectrum is not None:
                    self.componentButton = Button(self, text=spectrum.id)  #,toggle=True)
                    self.componentButton.clicked.connect(partial(self._toggleComponentButton, spectrum, sample, self.componentButton))
                    # self.componentButton.setChecked(False)
                    self.componentButton.setFixedHeight(40)
                    self.toolBarComponents.addWidget(self.componentButton)

    def _toggleComponentButton(self, spectrum, sample, componentButton):
        '''  Toggling the component button will populate the peak table and display the molecule on compoundViewer '''

        self.mainWindow.clearMarks()
        pressedButton = self.sender()

        buttons = []
        for item in pressedButton.parent().children():
            if hasattr(item, 'callback'):
                if item != componentButton:
                    buttons.append(item)

        for peakList in spectrum.peakLists:
            self.peakListObjects.append(peakList.peaks)
            self.peakTable.setObjects(self.peakListObjects[-1])

        for sampleComponent in sample.sampleComponents:
            if sampleComponent.substance is not None:
                if len(sampleComponent.substance.referenceSpectra) > 0:
                    if sampleComponent.substance.referenceSpectra[0] == spectrum:
                        smiles = sampleComponent.substance.smiles
                        if smiles is not None:
                            self.compoundView = CompoundView(self, smiles=smiles, preferences=self.preferences)
                            self.tabPeaksMoleculeLayout.addWidget(self.compoundView, 1, 1)
                            self.compoundView.resetView()

    ''' ######## ======== Second Tab properties (Multiple Compound View ====== ########   '''

    def _displayMolecules(self, sample):
        '''  displays the molecules on compoundViewers '''
        self._clearTabMoleculeView(sample)

        for component in sample.sampleComponents:
            if component.substance is not None:
                chemicalName = (''.join(str(x) for x in component.substance.synonyms))

                smiles = component.substance.smiles
                if smiles is not None:
                    self.compoundViewTab2 = CompoundView(self, smiles=smiles, preferences=self.preferences)
                    self.compoundViewTab2.setMaximumWidth(180)
                    self.tabMoleculeViewLayout.addWidget(self.compoundViewTab2)
                    self.compoundViewTab2.resetView()

    def _clearTabMoleculeView(self, sample):
        ''' Delete all the buttons if a different mixture is selected on the scoring table '''
        layout = self.tabMoleculeViewLayout
        items = [layout.itemAt(i) for i in range(layout.count())]
        if len(items) > 0:
            for item in items:
                item.widget().deleteLater()

    ''' ######## ======== 3Th Tab properties ====== ########   '''

    def _widgetsTabComponentsInfo(self):
        ''' creates a table with the relevant information about the substances/component in the mixture '''
        columns = [Column('Name', lambda substance: str(substance.pid)),
                   Column('logP', lambda substance: str(substance.logPartitionCoefficient)),
                   Column('psa', lambda substance: str(substance.polarSurfaceArea)),
                   Column('H acceptors', lambda substance: str(substance.hBondAcceptorCount)),
                   Column('H donors', lambda substance: str(substance.hBondDonorCount)),
                   Column('MW', lambda substance: str(substance.molecularMass))]

        self.sampleInfoTable = ObjectTable(self, columns, objects=[])
        self.tabMoleculeInfoLayout.addWidget(self.sampleInfoTable)

    def _displayMixturesInfo(self, sample):
        ''' fill the  sampleInfoTable  '''
        self.sampleComponents = sample.sampleComponents
        substances = [sc.substance for sc in self.sampleComponents]
        self.sampleInfoTable.setObjects(substances)

    ''' ###### ==== Fourth Tab properties (mixtureManagement) === ####
      This tab is made by two widget lists. Each widget list has the spectra present in the respective mixture.
      Left mixture is the selected on the scoring table. A pullDown lets select to create a new empty mixture or pick an other
      from the project.
      Moving spectra across by drag and drop allows the users to recreate manually the mixtures.'''

    def _mixtureManagementWidgets(self):
        ''' creates all the widgets present in the mixture Management tab '''
        currentMixture = self.scoringTable.getCurrentObject()
        self.contextMenu = Menu('', self, isFloatWidget=True)
        self.contextMenu.addItem("", callback=None)
        self.leftListWidget = ListWidget(self, contextMenu=False, copyDrop=False)

        self.rightListWidget = ListWidget(self, contextMenu=False, copyDrop=False)
        self.calculateButtons = ButtonList(self, texts=['Reset', 'Predict', 'Apply'],
                                           callbacks=[self._resetMixtureScore, self._predictScores, self._createNewMixture],
                                           tipTexts=[None, 'CLick to predict new mixtures', None], direction='h', hAlign='r')

        self.applyButtons = ButtonList(self, texts=['Cancel'],
                                       callbacks=[self._resetInitialState],
                                       tipTexts=[None], direction='h', hAlign='r')
        self.warningLabel = Label(self, 'Cancel or Apply to continue')

        self.pullDownSelection = PulldownList(self, )
        self.leftMixtureLineEdit = LineEdit(self, '')
        self.rightMixtureLineEdit = LineEdit(self, '')
        self.rightListWidget.setAcceptDrops(True)
        self.leftListWidget.setAcceptDrops(True)

        self.tabMixturesManagementLayout.addWidget(self.pullDownSelection, 0, 1)
        self.tabMixturesManagementLayout.addWidget(self.leftMixtureLineEdit, 1, 0)
        self.tabMixturesManagementLayout.addWidget(self.rightMixtureLineEdit, 1, 1)
        self.tabMixturesManagementLayout.addWidget(self.leftListWidget, 2, 0)
        self.tabMixturesManagementLayout.addWidget(self.rightListWidget, 2, 1)
        self.tabMixturesManagementLayout.addWidget(self.calculateButtons, 3, 1)
        self.tabMixturesManagementLayout.addWidget(self.warningLabel, 3, 0)
        self.tabMixturesManagementLayout.addWidget(self.applyButtons, 3, 1)

        self.leftMixtureLineEdit.editingFinished.connect(self._changeLeftMixtureName)
        self.rightMixtureLineEdit.editingFinished.connect(self._changeRightMixtureName)

        self.calculateButtons.buttons[2].setEnabled(False)

        self._disableRecalculateButtons()
        self.applyButtons.hide()
        self.warningLabel.hide()
        self.leftListWidget.contextMenuItem = 'Not Implemented Yet'

    def _populateLeftListWidget(self):
        ''' fills the left widget with spectra scores from the selected mixture on the scoring table '''
        sample = self.scoringTable.getCurrentObject()
        self.leftListWidget.clear()
        if sample is not None:
            self.leftMixtureLineEdit.setText(str(sample.name))
            color = QtGui.QColor('Red')
            header = QtWidgets.QListWidgetItem(str(sample.pid))
            header.setFlags(QtCore.Qt.NoItemFlags)
            # header.setTextColor(color)
            self.leftListWidget.addItem(header)
            for sampleComponent in sample.sampleComponents:
                if sampleComponent.substance is not None:
                    if len(sampleComponent.substance.referenceSpectra) > 0:
                        spectrum = sampleComponent.substance.referenceSpectra[0]
                        if spectrum is not None:
                            item = QtWidgets.QListWidgetItem(str(spectrum.pid) + ' Single Score = ' + str(sampleComponent.score))
                            self.leftListWidget.addItem(item)

                #   self.leftListWidget.addItem(item)
        self.rightListWidget.dropped.connect(self._itemsDropped)
        self.leftListWidget.dropped.connect(self._itemsDropped)

        # self.connect(self.rightListWidget, QtCore.SIGNAL("dropped"), self._itemsDropped)
        # self.connect(self.leftListWidget, QtCore.SIGNAL("dropped"), self._itemsDropped)
        self.leftListWidget.currentItemChanged.connect(self._itemClicked)

    def _populatePullDownSelection(self):
        ''' fills the pulldown with the mixtures on the project (excludes the one already selected on the left listWidget)  '''
        currentMixture = self.scoringTable.getCurrentObject()
        self.dataPullDown = ['Select An Option', 'New empty mixture']
        for mixture in self._getVirtualSamples():
            if mixture.name != currentMixture.name:
                self.dataPullDown.append(mixture.name)
        self.pullDownSelection.setData(self.dataPullDown)
        self.pullDownSelection.activated[str].connect(self._pullDownSelectionAction)

    def _pullDownSelectionAction(self, selected):
        ''' Each selection gives different behaviour on the right listWidget.
         '''
        if selected == 'New empty mixture':
            self.rightListWidget.clear()
            self.rightListWidget.setEnabled(True)
            self.leftListWidget.setEnabled(True)
            self.rightMixtureLineEdit.setText('NewMixture')

        if selected == 'Select An Option':
            self._selectAnOptionState()
            self._populateLeftListWidget()
            self.rightListWidget.setEnabled(False)
            self.leftListWidget.setEnabled(False)

        else:
            sample = self.project.getByPid('SA:' + selected)
            if sample is not None:
                self._populateRightListWidget(sample)
                self.rightListWidget.setEnabled(True)
                self.leftListWidget.setEnabled(True)

    def _populateRightListWidget(self, sample):
        ''' fills the right widget with spectra scores from the selected mixture on the pulldown '''
        if sample is not None:
            self.rightMixtureLineEdit.setText(str(sample.name))
            self.rightListWidget.clear()
            color = QtGui.QColor('Red')
            header = QtWidgets.QListWidgetItem(str(sample.name))
            header.setFlags(QtCore.Qt.NoItemFlags)
            # header.setTextColor(color)
            self.rightListWidget.addItem(header)
            for sampleComponent in sample.sampleComponents:
                if sampleComponent.substance is not None:
                    if len(sampleComponent.substance.referenceSpectra) > 0:
                        spectrum = sampleComponent.substance.referenceSpectra[0]
                        if spectrum is not None:
                            item = QtWidgets.QListWidgetItem(str(spectrum.pid) + ' Single Score = ' + str(sampleComponent.score))
                            self.rightListWidget.addItem(item)
            self.rightListWidget.currentItemChanged.connect(self._getListWidgetItems)

            # self.connect(self.rightListWidget, QtCore.SIGNAL("dropped"), self._itemsDropped)
            self.rightListWidget.dropped.connect(self._itemsDropped)
            self.rightListWidget.currentItemChanged.connect(self._itemClicked)

    def _getListWidgetItems(self):  # to do shorter
        '''Get  Spectra from the right ListWidget '''
        itemsRightWidgetList = []
        rightSpectra = []
        for index in range(self.rightListWidget.count()):
            itemsRightWidgetList.append(self.rightListWidget.item(index))
        for item in itemsRightWidgetList:
            itemText = item.text()
            text, space, value = itemText.partition(' ')
            rightSpectrum = self.project.getByPid(text)
            if rightSpectrum is not None:
                rightSpectra.append(rightSpectrum)

        '''Get Spectra from the left ListWidget '''
        itemsLeftWidgetList = []
        leftSpectra = []
        for index in range(self.leftListWidget.count()):
            itemsLeftWidgetList.append(self.leftListWidget.item(index))
        for item in itemsLeftWidgetList:
            itemText = item.text()

            text, space, value = itemText.partition(' ')
            leftSpectrum = self.project.getByPid(text)
            if leftSpectrum is not None:
                leftSpectra.append(leftSpectrum)

        return {'leftSpectra': leftSpectra, 'rightSpectra': rightSpectra}

    def _getListWidgetItemsTest(self, listWidget):
        items = []
        for index in range(listWidget.count()):
            items.append(listWidget.item(index))
        return (items)

    def _deleteComponent(self):
        selected = self.leftListWidget.currentRow()
        self.leftListWidget.takeItem(selected)

    def _deleteMixture(self):
        ''' delete the mixture from the project '''
        sample = self.scoringTable.getCurrentObject()
        if sample is not None:
            sample.delete()
        self._upDateScoringTable()

    def _upDateScoringTable(self):
        ''' refresh the scoring table '''
        self.scoringTable.setObjects(self._getVirtualSamples())

    def _createNewMixture(self):
        ''' create new mixtures after the items have been moved across the list widgets or a new empty mixture has been selected '''
        getLeftSpectra = self._getListWidgetItems()['leftSpectra']
        getRightSpectra = self._getListWidgetItems()['rightSpectra']

        oldLeftMixture = self.scoringTable.getCurrentObject()
        oldRightMixture = self._getMixtureFromPullDown()

        leftMixtureName = str(self.leftMixtureLineEdit.text())
        rightMixtureName = str(self.rightMixtureLineEdit.text())

        if self.pullDownSelection.getText() == 'New empty mixture':
            rightMixtureName = 'Mixture-' + str(len(self._getVirtualSamples()) + 1)
            mixtures = {leftMixtureName: self.leftCompounds, rightMixtureName: self.rightCompounds}
            oldLeftMixture.delete()
            _createSamples(self.project, mixtures, self.minimalDistance)

        else:
            mixtures = {leftMixtureName: self.leftCompounds, rightMixtureName: self.rightCompounds}
            oldRightMixture.delete()
            oldLeftMixture.delete()
            _createSamples(self.project, mixtures, self.minimalDistance)

        self._confirmNewMixtures()

    def _itemsDropped(self):
        ''' Returns the event of dropping data '''
        self._changeButtonStatus()

    def _itemClicked(self, item):
        ''' mouse left click, return the item clicked'''
        pass

    def _predictScores(self):  # to do
        ''' Predict scores before to create a different mixture given the left spectra '''
        leftSpectra = self._getListWidgetItems()['leftSpectra']
        self.leftCompounds = _getCompounds(leftSpectra)
        leftComponentsScores = self.temporarySampleComponentsScore(self.leftCompounds, self.minimalDistance)
        # self.leftListWidget.clear()
        header = QtWidgets.QListWidgetItem(
                'Predicted Tot Score' + str(round(scoreMixture(self.leftCompounds, self.minimalDistance), 2)))
        header.setFlags(QtCore.Qt.NoItemFlags)
        # header.set(QtGui.QColor('Red'))
        self.leftListWidget.addItem(header)

        for i in leftComponentsScores:
            self.leftListWidget.addItem(i)

        rightSpectra = self._getListWidgetItems()['rightSpectra']
        self.rightCompounds = _getCompounds(rightSpectra)
        rightComponentsScores = self.temporarySampleComponentsScore(self.rightCompounds, self.minimalDistance)
        self.rightListWidget.clear()

        header = QtWidgets.QListWidgetItem('Predicted Tot Score' + str(round(scoreMixture(self.rightCompounds, self.minimalDistance), 2)))
        header.setFlags(QtCore.Qt.NoItemFlags)
        # header.setTextColor(QtGui.QColor('Red'))
        self.rightListWidget.addItem(header)
        for i in rightComponentsScores:
            self.rightListWidget.addItem(i)

        self.calculateButtons.buttons[1].setEnabled(False)

        self.calculateButtons.buttons[2].setEnabled(True)

    def temporarySampleComponentsScore(self, mixtureCompounds, minDist):
        self.componentsScores = []
        for compound in mixtureCompounds:
            compoundName, compoundPeakList = compound
            compoundsToCompare = [c[1] for c in mixtureCompounds if c[0] != compoundName]
            overlaped = calculateOverlapCount(compoundPeakList, compoundsToCompare, minDist)

            if overlaped is None:
                self.componentsScores.append(str(compoundName) + ' temp Score= 0')

            else:
                score = len(overlaped) / len(compoundPeakList)
                self.componentsScores.append(str(compoundName) + ' temp Score= ' + str(round(score, 2)))
        return self.componentsScores

    def _temporaryScoringStatus(self):  # to do shorter
        ''' Disable all the commands so user is forced to take a decision with the new scoring after a mixture has been recalculated '''
        pass
        # self.pullDownSelection.setEnabled(False)
        # for i in range(3):
        #   self.tabWidget.setTabEnabled(i,False)
        # self.calculateButtons.hide()
        # self.applyButtons.show()
        # self.rightListWidget.setAcceptDrops(False)
        # self.leftListWidget.setAcceptDrops(False)
        # for item in self._getListWidgetItemsTest(self.leftListWidget):
        #   item.setFlags(QtCore.Qt.NoItemFlags)
        # for item in self._getListWidgetItemsTest(self.rightListWidget):
        #   item.setFlags(QtCore.Qt.NoItemFlags)
        # self.warningLabel.show()
        # self.scoringTable.selectionCallback = None
        # print('Selection Table Disabled. Cancel or apply the new mixtures scores')

    def _confirmNewMixtures(self):  # to do shorter
        ''' restore the normal behavior if the buttons '''

        self._upDateScoringTable()
        self._selectAnOptionState()
        self._populateLeftListWidget()

    def _resetMixtureScore(self):
        ''' restore the first scores calculated  '''
        self._resetInitialState()

    def _getMixtureFromPullDown(self):
        ''' Documentation '''
        currentPullDownSelection = self.pullDownSelection.getText()
        mixturePullDown = self.project.getByPid('SA:' + currentPullDownSelection)
        if mixturePullDown is not None:
            return mixturePullDown

    def _resetInitialState(self):
        ''' clears up the right listWidget and restores the buttons  '''
        for i in range(3):
            self.tabWidget.setTabEnabled(i, True)
        self.pullDownSelection.setEnabled(True)
        self._selectAnOptionState()
        self.calculateButtons.show()
        self._disableRecalculateButtons()
        self.applyButtons.hide()
        self.warningLabel.hide()
        self._populateLeftListWidget()
        self.scoringTable.selectionCallback = self._tableSelection

    def _changeLeftMixtureName(self):
        ''' changes the mixture name '''
        currentMixture = self.scoringTable.getCurrentObject()
        if self.leftMixtureLineEdit.isModified():
            currentMixture.rename(self.leftMixtureLineEdit.text())

    def _changeRightMixtureName(self):
        ''' changes the mixture name '''
        currentPullDownSelection = self.pullDownSelection.getText()
        mixturePullDown = self.project.getByPid(currentPullDownSelection)
        if mixturePullDown is not None:
            if self.rightMixtureLineEdit.isModified():
                mixturePullDown.rename(self.rightMixtureLineEdit.text())

    def _initialLabelListWidgetRight(self):
        ''' Creates an initial message on the right ListWidget '''
        item = QtWidgets.QListWidgetItem(' Drag and drop items across to calculate the new scores')
        item.setFlags(QtCore.Qt.NoItemFlags)
        self.rightListWidget.addItem(item)

    def _selectAnOptionState(self):
        ''' Creates an initial status on the right ListWidget '''
        self.pullDownSelection.select('Select An Option')
        self.rightListWidget.clear()
        self.rightListWidget.setEnabled(False)
        self.leftListWidget.setEnabled(False)
        self._initialLabelListWidgetRight()
        self._disableRecalculateButtons()
        self.rightMixtureLineEdit.setText('')

    def _disableRecalculateButtons(self):
        ''' disables the buttons until a change occurs  '''
        for button in self.calculateButtons.buttons:
            button.setEnabled(False)
            # button.setStyleSheet("background-color:#868D9D; color: #000000")

    def _changeButtonStatus(self):
        ''' enables the buttons when a change occurs '''
        for button in self.calculateButtons.buttons:
            button.setEnabled(True)
            # if self.colourScheme == 'dark':
            #   button.setStyleSheet("background-color:#535a83; color: #bec4f3")
            # else:
            #  button.setStyleSheet("background-color:#bd8413; color: #fdfdfc")
        self.calculateButtons.buttons[2].setEnabled(False)

    ''' ######## ==== Gui Spectrum View properties  ====  ########   '''

    def _displayMixture(self, sample):
        ''' displays all the spectra present in a mixture '''
        strip = self._clearDisplayView()
        for sampleComponent in sample.sampleComponents:
            if sampleComponent.substance is not None:
                if len(sampleComponent.substance.referenceSpectra) > 0:
                    strip.spectrumDisplay.displaySpectrum(sampleComponent.substance.referenceSpectra[0])
                else:
                    spectrum = self.project.getByPid('SP:' + str(sampleComponent.substance.name))
                    if spectrum is not None:
                        strip.spectrumDisplay.displaySpectrum(spectrum)

    def _clearDisplayView(self):
        ''' Deletes all the spectra from the display '''
        if self.current.strip is None:
            if len(self.project.strips) > 0:
                strip = self.project.strips[0]
                self.current.strip = strip
                self.current.strip._maximiseRegions()
            else:
                strip = self._openNewDisplay()
        else:
            strip = self.current.strip
        for spectrumView in strip.spectrumViews:
            spectrumView.delete()
        return strip

    def _openNewDisplay(self):
        ''' opens a new spectrum display '''

        if len(self.project.spectra) > 0:
            spectrumDisplay = self.mainWindow.createSpectrumDisplay(self.project.spectra[0])
            if len(spectrumDisplay.strips) > 0:
                self.current.strip = spectrumDisplay.strips[0]
                self.current.strip._maximiseRegions()
            self.moduleArea.moveModule(spectrumDisplay, position='top', neighbor=self)
            return spectrumDisplay


    ''' ######## ==== Settings  ====  ########   '''

    def _createSettingGroup(self):
        '''GroupBox creates the settingGroup'''
        self.settingButtons = ButtonList(self, texts=['', '', ],
                                         callbacks=[self._exportMixturesToXlsx, self._openOptimisationModule], icons=[self.exportIcon, self.settingIcon, ],
                                         tipTexts=['', ''], direction='H')
        self.settingButtons.setStyleSheet("background-color: transparent")
        self.settingFrameLayout.addStretch(1)
        self.settingFrameLayout.addWidget(self.settingButtons)

    # def exportToXls(self):
    # ''' Export a simple xlxs file from the results '''
    # self.nameAndPath = ''
    # fType = 'XLS (*.xlsx)'
    # dialog = QtWidgets.QFileDialog
    # filePath = dialog.getSaveFileName(self,filter=fType)
    # self.nameAndPath = filePath
    #
    # sampleColumn = [str(sample.pid) for sample in self.project.samples]
    # sampleComponents = [str(sample.spectra) for sample in self.project.samples]
    # df = DataFrame({'Mixture name': sampleColumn, 'Sample Components': sampleComponents})
    # df.to_excel(self.nameAndPath, sheet_name='sheet1', index=False)
    # def closeModule(self):
    #
    #   for module in self.moduleArea.findAll()[1].values():
    #     if module.label.isHidden():
    #       module.close()
    #   self.close()
    def _exportMixturesToXlsx(self):
        ''' Export a simple xlxs file from the results '''
        dataFrame = self.createMixturesDataFrame()

        fType = 'XLSX (*.xlsx)'
        # FIXME
        dialog = QtWidgets.QFileDialog
        filePath = dialog.getSaveFileName(self, filter=fType)
        if len(filePath) > 0:
            dataFrame.to_excel(filePath[0], sheet_name='Mixtures', index=False)

    def _openOptimisationModule(self):
        mixtureOptimisation = MixtureOptimisation(mainWindow=self.mainWindow, virtualSamples=self._getVirtualSamples(),
                                                  mixtureAnalysisModule=self, minimalDistance=self.minimalDistance, )

        mixtureOptimisationModule = self.moduleArea.addModule(mixtureOptimisation, position='bottom')

    def createMixturesDataFrame(self):
        from pandas import DataFrame

        sampleColumn = [str(sample.pid) for sample in self.project.samples if sample.isVirtual]
        sampleComponents = [str(sample.spectra) for sample in self.project.samples]
        df = DataFrame({'Mixture': [c.id for c in self.project.sampleComponents if c.sample.isVirtual]})

        return df


if __name__ == '__main__':
    from ccpn.ui.gui.widgets.Application import TestApplication
    from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea


    app = TestApplication()

    win = QtWidgets.QMainWindow()

    moduleArea = CcpnModuleArea(mainWindow=None, )
    module = MixtureAnalysis(mainWindow=None)
    moduleArea.addModule(module)

    win.setCentralWidget(moduleArea)
    win.resize(1000, 500)
    win.setWindowTitle('Testing %s' % module.moduleName)
    win.show()

    app.start()
