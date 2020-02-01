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
__version__ = "$Revision: 3.0.0 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt5 import QtCore, QtGui, QtWidgets
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.CompoundView import CompoundView
from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.LinearRegionsPlot import LinearRegionsPlot
from ccpn.ui.gui.widgets.Column import ColumnClass, Column

from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.modules.PeakTable import PeakListTableWidget
from ccpn.ui.gui.modules.PeakTable import PeakListTableWidget as pltw
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.widgets.Frame import Frame
from ccpn.ui.gui.widgets.Button import Button
from ccpn.ui.gui.widgets.FileDialog import FileDialog
from ccpn.ui.gui.widgets.Spacer import Spacer
from functools import partial
from ccpn.core.SpectrumHit import SpectrumHitPeakList
from ccpn.core.lib.Notifiers import Notifier
from ccpn.ui.gui.widgets.GuiTable import GuiTable
from ccpn.AnalysisScreen.pipes.HitsOutput import hitsToDataFrame, DeltaPositions, ReferencePeakPositions, ExperimentTypeName,ReferenceFigureOfMerit, ReferenceLevel, ReferencePid, SpectrumHitPid
# from ccpn.ui.gui.widgets.tableTest import DataFrameWidget
from ccpn.util.Common import makeIterableList
from ccpn.ui.gui.widgets.Splitter import Splitter

Qt = QtCore.Qt
Qkeys = QtGui.QKeySequence

ListWidgetHeaderColor = QtGui.QColor('Red')

ReferenceLabel = 'Reference Details: '
ALL_ExperimentTypes = 'All'
ExperimentTypesDict = {
    'STD': 'STD.H',
    'Water-LOGSY': 'Water-LOGSY.H',
    'H': 'H',
    't1rho': 'H[t1rho(H)]',
    ALL_ExperimentTypes: None
    }


class HitsAnalysis(CcpnModule):
    includeSettingsWidget = True
    maxSettingsState = 2
    settingsPosition = 'left'
    className = 'ScreeningHits'

    def __init__(self, mainWindow, name='Hit Analysis', **kwds):
        super(HitsAnalysis, self)
        CcpnModule.__init__(self, mainWindow=mainWindow, name=name)

        self._spectrumHits = []
        self._reference = None  #selected ref spectrum on hit table
        self.application = None
        self.project = None
        self.current = None
        self.preferences = None
        self.hitsData = None
        self.__peaksDict = {}

        if mainWindow is not None:
            self.mainWindow = mainWindow
            self.project = self.mainWindow.project
            self.application = self.mainWindow.application
            self.moduleArea = self.mainWindow.moduleArea
            self.preferences = self.application.preferences
            self.current = self.application.current
            self._spectrumHits = self.project.spectrumHits

        ######## ======== Icons ====== ########

        self.nextIcon = Icon('icons/sort-down')
        self.previousIcon = Icon('icons/sort-up')
        self.minusIcon = Icon('icons/minus')
        self.plusIcon = Icon('icons/plus')
        self.rejectIcon = Icon('icons/reject')
        self.acceptIcon = Icon('icons/dialog-apply')
        self._showHitRegion = False
        self._markHitPositions = False
        self._createWidgets()
        self._createSettingsWidgets()

        # set notifier
        if self.project is not None:
            self._spectrumHitNotifier = Notifier(self.project, [Notifier.DELETE, Notifier.CREATE, Notifier.CHANGE],
                                                 'SpectrumHit', self._spectrumHitNotifierCallback)

    def _createWidgets(self):
        ''' Documentation '''

        # self.mainWidget.setContentsMargins(10,10,10,10)
        self._hsplitter = Splitter(setLayout=False, horizontal=False)
        self._h2splitter = Splitter(setLayout=False, horizontal=False)
        self._vsplitter = Splitter(setLayout=False, horizontal=True)
        ## Set ExperimentType Frame
        column = 0
        self.experimentTypeWidgetsFrame = Frame(self.settingsWidget, setLayout=True, margins=(10, 10, 10, 10),
                                                grid=(1, column))
        column += 1
        self.spectrumHitWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10, 10, 10, 10),
                                             grid=(0, column),gridSpan=(0, 1))#, gridSpan=(2, column)gridSpan=(0, 1))
        # self.spectrumHitWidgetsFrame.setMinimumWidth(200)

        column += 1
        self.peakHitWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10, 10, 10, 10),
                                         grid=(0, column),gridSpan=(0, 1))
        # self.peakHitWidgetsFrame.setMinimumWidth(300)
        # column += 1
        self.referenceWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10, 10, 10, 10),
                                           grid=(0, column),gridSpan=(0, 1))
        # self.referenceWidgetsFrame.setMinimumWidth(300)
        column += 1
        self.substanceDetailsFrame = Frame(self.mainWidget, setLayout=True, margins=(10, 10, 10, 10),
                                           grid=(0, column), gridSpan=(0, 1))
        # self.substanceDetailsFrame.hide()
        self._h2splitter.addWidget(self.spectrumHitWidgetsFrame)
        self._hsplitter.addWidget(self.substanceDetailsFrame)
        self._vsplitter.addWidget(self.peakHitWidgetsFrame)
        self._vsplitter.addWidget(self.referenceWidgetsFrame)
        self._vsplitter.addWidget(self._hsplitter)
        self._h2splitter.addWidget(self._vsplitter)
        self.mainWidget.getLayout().addWidget(self._h2splitter)

        # self.vBarTableSplitter.addWidget(self.spectrumHitWidgetsFrame)
        # self.hPlotsTableSplitter.addWidget(self.peakHitWidgetsFrame)
        # self.hPlotsTableSplitter.addWidget(self.referenceWidgetsFrame)
        # self.vBarTableSplitter.setStretchFactor(0, 1)
        # self.mainWidget.getLayout().addWidget(self.vBarTableSplitter)

        self._setExperimentTypeWidgets()
        self._setSpectrumHitWidgets()
        self._setPeakHitWidgets()
        self._setReferenceHitWidgets()
        self._setSubstanceDetailsWidgets()
        self._setSpectrumHitTable()

    def _setExperimentTypeWidgets(self):
        self.experimentTypeLabel = Label(self.settingsWidget, text='Experiment Type',
                                         grid=(0, 1), vAlign='t', )

        self.experimentTypeRadioButtons = RadioButtons(self.settingsWidget,
                                                       texts=sorted(list(ExperimentTypesDict.keys())),
                                                       callback=self._showBytExperimentType,
                                                       direction='V',
                                                       grid=(1, 1))
        self.experimentTypeWidgetsFrame.getLayout().setAlignment(Qt.AlignTop)

    def _setSpectrumHitWidgets(self):

        self.HitTableLabel = Label(self.spectrumHitWidgetsFrame, text='Hits Scores', vAlign='t', grid=(0, 0))
        self.hitTable = GuiTable(self.spectrumHitWidgetsFrame, mainWindow=self.mainWindow,
                                 selectionCallback=self._setCurrentSpectrumHit,
                                 actionCallback=self._openSpectrumHitOnNewDiplay,
                                 grid=(1, 0), vAlign='t',hPolicy='expanding')


        # self.HitTableLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.hitButtons = ButtonList(self.spectrumHitWidgetsFrame, texts=['', '','', '', '', ''],
                                     callbacks=[partial(self._movePreviousRow, self.hitTable),
                                                self._deleteReference,
                                                None,
                                                partial(self._setHitIsConfirmed, False),
                                                partial(self._setHitIsConfirmed, True),
                                                partial(self._moveNextRow, self.hitTable)],
                                     icons=[self.previousIcon, self.minusIcon,self.plusIcon, self.rejectIcon, self.acceptIcon, self.nextIcon],
                                     tipTexts=[None, None, None, None, None, None],
                                     direction='V', vAlign='t',
                                     grid=(1, 1))
        self.hitButtons.setFixedWidth(80)
        #
        # self.hitButtons.hide()

    def _createMarksOnPeakHits(self):
        if self._markHitPositions:
            self.project.deleteObjects(*self.project.marks)
            for p in self.current.spectrumHit._getPeakHits():
                self.project.newMark(colour=p.peakList.spectrum.sliceColour, positions=p.position,
                                     axisCodes=p.peakList.spectrum.axisCodes)

    @staticmethod
    def _getSelectedObject(table, row, headerName):
        '''
        :param headerName: PID Str header name as in dataFrame
        :return: object
        '''
        obj = None
        for i in range(table.horizontalHeader().count()):
            if table.horizontalHeaderItem(i).text() == headerName:
                pid = table.item(row, i).text()
                obj = table.project.getByPid(pid)
        return obj

    def _openSpectrumHitOnNewDiplay(self, data):
        from ccpn.ui.gui.lib.MenuActions import _openItemObject
        row = data.get('row')

        spectrumHit = self._getSelectedObject(self.hitTable, row, SpectrumHitPid)
        spectrum = self._getSelectedObject(self.hitTable, row, ReferencePid)
        if spectrum and spectrumHit:
            _openItemObject(self.mainWindow, [spectrumHit.spectrum, spectrum])



    def _setPeakHitWidgets(self):
        self.peakHitTableLabel = Label(self.peakHitWidgetsFrame, text='Target Peak Hits', vAlign='t',
                                       grid=(0, 0))

        self.targetPeakTable = GuiTable(self.peakHitWidgetsFrame,
                                         selectionCallback=self._selectionTargetPeakCallback,
                                         actionCallback=self._actionTargetPeakCallback,
                                         multiSelect=False, selectRows=True,
                                                     mainWindow=self.mainWindow,
                                                     grid=(1, 0))
        self._setTPT(self.targetPeakTable)
        self.peakButtons = ButtonList(self.peakHitWidgetsFrame, texts=['', '','', '', ],
                                      callbacks=[partial(self._movePreviousRow, self.targetPeakTable),
                                                 partial(self._deletePeaks, self.targetPeakTable),
                                                 None,
                                                 partial(self._moveNextRow, self.targetPeakTable)],
                                      icons=[self.previousIcon, self.minusIcon, self.plusIcon, self.nextIcon],
                                      tipTexts=[None, None,None, None],
                                      direction='H', vAlign='b',
                                      grid=(2, 0))

    @staticmethod
    def _getCommentText(obj):
        """
        CCPN-INTERNAL: Get a comment from GuiTable
        """
        try:
            if obj.comment == '' or not obj.comment:
                return ''
            else:
                return obj.comment
        except:
            return ''

    @staticmethod
    def _setComment(obj, value):
        """
        CCPN-INTERNAL: Insert a comment into GuiTable
        """
        # ejb - why is it blanking a notification here?
        # NmrResidueTable._project.blankNotification()
        obj.comment = value if value else None
        # NmrResidueTable._project.unblankNotification()

    def _setTPT(self, table):

        table.positionsUnit = 'ppm'
        table._getCommentText = self._getCommentText
        table._setComment = self._setComment
        table._hiddenColumns = ['Pid', 'Id']
        table.setMinimumHeight(150)


    def _actionTargetPeakCallback(self, *data):
        peaks = self.targetPeakTable.getSelectedObjects()
        if len(peaks)>0:
            if self.current.strip:
                self._navigateToPeakPosition(self.current.strip, peaks[0])

    def _actionReferencePeakCallback(self, *data):
        peaks = self.referencePeakTable.getSelectedObjects()
        if len(peaks)>0:
            if self.current.strip:
                self._navigateToPeakPosition(self.current.strip, peaks[0])

    def _navigateToPeakPosition(self, strip, peak):
        from ccpn.ui.gui.lib.Strip import navigateToPositionInStrip, _getCurrentZoomRatio

        if strip is not None:
            widths = _getCurrentZoomRatio(strip.viewRange())
            navigateToPositionInStrip(strip=strip, positions=peak.position, widths=widths)

    def _populateTable(self, table, peaks, peakList ):

        table.populateTable(rowObjects=peaks,
                                           columnDefs=pltw._getTableColumns(table, peakList))

    def _setReferenceHitWidgets(self):

        # self.referencePeakTableLabel = Label(self.referenceWidgetsFrame, text='Matched Reference Peak', vAlign='t',
        #                                      grid=(0, 0))


        self.referencePeakTable = GuiTable(self.referenceWidgetsFrame,
                                        selectionCallback=self._selectionReferencePeakCallback,
                                        actionCallback=self._actionReferencePeakCallback,
                                        multiSelect=False, selectRows=True,
                                        mainWindow=self.mainWindow,
                                        grid=(1, 0), vAlign='t')
        self._setTPT(self.referencePeakTable)

        self.referencePeakTableLabel = Label(self.referenceWidgetsFrame, text='Matched Reference Peak', vAlign='t',
                                             grid=(0, 0))
        self.referenceButtons = ButtonList(self.referenceWidgetsFrame, texts=['', '', '', '' ],
                                      callbacks=[partial(self._movePreviousRow,self.referencePeakTable),
                                                 None,
                                                 None,
                                                 partial(self._movePreviousRow,self.referencePeakTable)],
                                      icons=[self.previousIcon, self.minusIcon, self.plusIcon, self.nextIcon],
                                      tipTexts=[None, None,None, None],
                                      direction='H', vAlign='b',
                                      grid=(2, 0))

    def _setSubstanceDetailsWidgets(self):

        self.substanceDetailsLabel = Label(self.substanceDetailsFrame, text=ReferenceLabel,
                                           grid=(0, 0))
        self.compoundView = CompoundView(self.substanceDetailsFrame, preferences=self.preferences, smiles=[],  #hAlign='t',vAlign='t',
                                         grid=(1, 0))
        self.compoundView.setMinimumHeight(100)
        self.listWidgetsHitDetails = ListWidget(self.substanceDetailsFrame, contextMenu=False,  #hAlign='t',vAlign='t',
                                                grid=(2, 0))

    @property
    def hitsData(self):
        """ currently displayed data as pandas DataFrame  """
        return self._hitsData

    @hitsData.getter
    def hitsData(self):
        if self._hitsData is None:
            hd = hitsToDataFrame(self.project, self._spectrumHits)
            self._hitsData = hd
        else:
            hd = self._hitsData
        return hd

    @hitsData.setter
    def hitsData(self, df):
        self._hitsData = df


    def _dfCell__ListsToStrs(self, df, dfColumnName):
        """Pandas specific. flatten a list of list present in a pandas row cell to one single list.
         Convert the list to strs without brackets,  to display on a table"""
        vv = [(makeIterableList(b[dfColumnName])) for i, b in df.iterrows()]
        return [', '.join(str(i) for i in v) for v in vv]

    def _setSpectrumHitTable(self, df=None):
        "Sets the SpectrumHitTable."
        if df is None:
            df = self.hitsData
        try:
            if df is not None:
                df[DeltaPositions] = self._dfCell__ListsToStrs(df, DeltaPositions) # it has to be a str for the table
                df[ReferencePeakPositions] = self._dfCell__ListsToStrs(df, ReferencePeakPositions)

                # df = df.drop_duplicates(subset='SpectrumHit', keep="last")
                self.hitTable.setData(df)
        except Exception as err:
            print('Hit Dataframe Error: ', err)


    def _getSerial(self, hit):
        return self._spectrumHits.index(hit) + 1

    def _createSettingsWidgets(self):
        self.settingsWidget.setContentsMargins(20, 20, 20, 20)
        row = 0
        self.targetPeaksCheckbox = CheckBox(self.settingsWidget, text='Target Peaks', checked=False,
                                            callback=partial(self._toggleFrame,
                                                             widget=self.peakHitWidgetsFrame),
                                            grid=(row, 0))
        row += 1
        self.referencePeaksCheckbox = CheckBox(self.settingsWidget, text='Reference Peaks', checked=False,
                                               callback=partial(self._toggleFrame,
                                                                widget=self.referenceWidgetsFrame),
                                               grid=(row, 0))
        row += 1
        self.substanceDetailsCheckbox = CheckBox(self.settingsWidget, text='Substance Details', checked=self._showHitRegion,
                                                 callback=partial(self._toggleFrame,
                                                                  widget=self.substanceDetailsFrame),
                                                 grid=(row, 0))
        row += 1
        self.hitRegionsCheckbox = CheckBox(self.settingsWidget, text='Hit Regions ', checked=True,
                                           callback=self._toggleMarks,
                                           grid=(row, 0))

        # Spacer(self.settingsWidget, 5, 5,
        #        QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding,
        #        grid=(row + 1, 2), gridSpan=(1, 1))

        #   Hide tables until fixed:
        # self.peakHitWidgetsFrame.hide()
        # self.referenceWidgetsFrame.hide()
        # self.substanceDetailsFrame.hide()
        # self.targetPeaksCheckbox.setEnabled(False)
        # self.referencePeaksCheckbox.setEnabled(False)
        # self.hitRegionsCheckbox.setEnabled(False)
        # self.substanceDetailsCheckbox.setEnabled(False)

    def _toggleMarks(self):
        if self.sender() is not None:
            if self.sender().isChecked():
                self._markHitPositions = True
            else:
                self._markHitPositions = False

    def _toggleFrame(self, widget):
        '''Specific to hide a widget from a checkbox callback  '''
        if self.sender() is not None:
            if self.sender().isChecked():
                widget.show()
            else:
                widget.hide()

    def _showBytExperimentType(self):
        "Shows hits by the experiment type of the spectrumHit.spectrum. If not Defined, only All is active"
        selectedExpType = self.experimentTypeRadioButtons.get()
        if self.project is not None:
            if selectedExpType == ALL_ExperimentTypes:
                self._spectrumHits = self.project.spectrumHits
                self._updateHitTable()
                return

            self._spectrumHits = []
            for spectrumHit in self.project.spectrumHits:
                experimentType = spectrumHit.spectrum.experimentType
                if experimentType == ExperimentTypesDict[selectedExpType]:
                    self._spectrumHits.append(spectrumHit)
            self._updateHitTable()

    def _selectionReferencePeakCallback(self, data, *args):
        """
        set as current the selected peaks on the table and populates the reference peak Table
        """

        peaks = data['object']
        print('Not implemented any yet')

    def _selectionTargetPeakCallback(self, data, *args):
        """
        set as current the selected peaks on the table and populates the reference peak Table
        """

        peaks = data['object']
        # self.targetPeakTable._selectionCallback(data, *args) #set currentPeaks
        if len(peaks)>0:
            peak = peaks[-1]
            self._populateReferencePeakTable(peak)

        # if peaks is not None:
        #     for peak in peaks:
        #         if len(peak._linkedPeaks) > 0:
        #             matchedPeak = peak._linkedPeaks[0]
        #
        #     if matchedPeak is not None:
        #         self._populateReferencePeakTable(matchedPeak)

    def _referencePeakTableCallback(self, data, *args):
        peaks = data['object']
        # self.referencePeakTable._selectionCallback(data, *args)
        if peaks is not None:
            for peak in peaks:
                if peak is not None:
                    spectrum = peak.peakList.spectrum
                    substance = spectrum.referenceSubstance
                    if substance is not None:
                        self._showHitInfoOnDisplay(substance)
                    else:
                        self._showSpectrumInfo(spectrum)


    def _clearSpectrumViews(self):
        if self.current is not None:
            if self.current.strip is not None:
                for i in self.current.strip.spectrumViews:
                    if i is not None:
                        i.delete()


    def _showSpectrumInfo(self, spectrum):
        self._clearListWidget()
        self.compoundView.setSmiles('h')
        self.substanceDetailsLabel.set(ReferenceLabel + spectrum.name)
        self.listWidgetsHitDetails.clear()
        header = QtWidgets.QListWidgetItem('\n No Substance Details Found')
        header.setFlags(QtCore.Qt.NoItemFlags)
        # header.setTextColor(ListWidgetHeaderColor)
        self.listWidgetsHitDetails.addItem(header)

    def _populateReferencePeakTable(self, peak):
        'populates the table only with matched peaks linked to the targetPeak'

        pass

        refPeaks = self.__peaksDict.get(peak)
        if refPeaks is not None:
            if len(refPeaks)>0:
                self._populateTable(self.referencePeakTable, refPeaks, refPeaks[0].peakList)

        # if peak is not None:
        #     referencePeakList = peak.peakList
        #     self.referencePeakTable.pLwidget.select(referencePeakList.pid)
        #     if referencePeakList is not None:
        #         self.referencePeakTable._updateTable(useSelectedPeakList=False, peaks=[peak])
        #     self.referencePeakTable.selectObjects([peak])
        #     self.current.peaks += (peak,)
        #     spectrum = peak.peakList.spectrum
        #     substance = spectrum.referenceSubstance
        #     if substance is not None:
        #         self._showHitInfoOnDisplay(substance)
        #     else:
        #         self._showSpectrumInfo(spectrum)

    def _setTargetPeakTable(self,spectrumHit, reference):
        self.referencePeakTable.clearTable()
        self.targetPeakTable.clearTable()
        if self.current.spectrumHit:
            targetPeakList = self._getTargetPeakList()
            peaksDd = spectrumHit._getPeaksForReference(reference)
            self.__peaksDict = peaksDd
            targetPeaks = list(peaksDd.keys())

            if len(targetPeaks)>0:
                # print('_setTargetPeakTable',spectrumHit, reference, targetPeakList, targetPeaks)
                self._populateTable(self.targetPeakTable, targetPeaks, targetPeaks[0].peakList)

        else:
            self.targetPeakTable.clearTable()

    def _getTargetPeakList(self):
        if self.current is not None:
            if self.current.spectrumHit is not None:
                for pl in self.current.spectrumHit.spectrum.peakLists:
                    if pl.isSimulated and pl.title == SpectrumHitPeakList:
                        return pl

    def _setHitIsConfirmed(self, value: bool):
        ''' Documentation '''
        if self.current is not None:
            hit = self.current.spectrumHit
            if hit is not None:
                hit.isConfirmed = value
                self._updateHitTable()

    def _setCurrentSpectrumHit(self, data):
        """
        set as current the selected spectrumHit on the table
        """

        row =  data.get('row')
        spectrumHit = self._getSelectedObject(self.hitTable, row, SpectrumHitPid)
        spectrum = self._getSelectedObject(self.hitTable, row, ReferencePid)

        self.current.spectrumHit = spectrumHit
        self._showHitOnStrip(spectrum)
        self._showHitInfoOnDisplay(spectrum.referenceSubstance)
        self._setTargetPeakTable(spectrumHit, spectrum)
        # self._createMarksOnPeakHits()

    def _showHitOnStrip(self, displaySpectrum=None, *args):
        if self.current.strip:
            self.current.strip._clear()
            d = self.current.strip.spectrumDisplay.displaySpectrum
            if self.current.spectrumHit:
                if displaySpectrum:
                    if self.current.strip:
                        d(self.current.spectrumHit.spectrum)
                        d(displaySpectrum)

    def _clearListWidget(self):
        ''' Documentation '''

        self.listWidgetsHitDetails.clear()

    def _commitMoveNextRow(self):
        ''' Documentation '''

        self._acceptAssignment()
        self._moveNextRow(self.hitTable)

    def _commitMovePreviousRow(self):
        ''' Documentation '''
        self._acceptAssignment()
        self._movePreviousRow(self.hitTable)

    def _deleteReference(self):
        if self._reference is not None:
            if self.current.spectrumHit is not None:
                self.current.spectrumHit._removeReference(self._reference)
        self._setSpectrumHitTable()

    def _deleteHit(self):
        ''' Deletes hit from project and from the table. If is last cleans all graphics
        '''
        if self.current is not None:
            spectrumHit = self.current.spectrumHit
            if spectrumHit is not None:
                targetPeakList = self._getTargetPeakList()
                if targetPeakList is not None:
                    targetPeakList.delete()
                spectrumHit.delete()

    def _deletePeaks(self, table):
        if table is not None:
            peaks = table.getSelectedObjects()
            if peaks:
                for peak in peaks:
                    if peak is not None:
                        peak.delete()

        self._updateHitTable()
        self.referencePeakTable.clearTable()




    def _getSampleInfoToDisplay(self, sample):
        ''' Documentation '''
        if sample is not None:
            sampleInfo = {'Name: ': sample.name,
                          'Amount: ': sample.amount,
                          'CreationDate: ': sample.creationDate,
                          'PlateIdentifier: ': sample.plateIdentifier,
                          'RowNumber: ': sample.rowNumber,
                          'ColumnNumber: ': sample.columnNumber,
                          'Comment: ': sample.comment, }
            return sampleInfo
        else:
            return {'Link to a Substance to display contents': ''}

    def _getSubstanceInfoToDisplay(self, substance):
        ''' Documentation '''
        if substance is not None:

            substanceInfo = {'name: ': substance.name,
                             'synonyms: ': substance.synonyms,
                             'userCode: ': substance.userCode,
                             'empiricalFormula: ': substance.empiricalFormula,
                             'molecularMass: ': substance.molecularMass,
                             'atomCount: ': substance.atomCount,
                             'bondCount: ': substance.bondCount,
                             'ringCount: ': substance.ringCount,
                             'hBondDonorCount: ': substance.hBondDonorCount,
                             'hBondAcceptorCount: ': substance.hBondAcceptorCount,
                             'polarSurfaceArea: ': substance.polarSurfaceArea,
                             'logPartitionCoefficien: ': substance.logPartitionCoefficient,
                             'comment: ': substance.comment}
            return substanceInfo

        else:
            return {'Link to a Substance to display contents': ''}

    def _moveNextRow(self, table):
        ''' Documentation '''

        self.currentRowPosition = table.getSelectedRows()
        try:
            if len(self.currentRowPosition) > 0:
                newPosition = self.currentRowPosition[0] + 1
                table.selectRow(newPosition)
                lastRow = len(table.objects) - 1
                if newPosition >= len(table.objects):
                    table.selectRow(0)
                else:
                    table.selectRow(newPosition)
            else:
                table.selectRow(0)
        except:
            pass

    def _movePreviousRow(self, table):
        ''' Documentation '''

        self.currentRowPosition = table.getSelectedRows()
        if len(self.currentRowPosition) > 0:
            newPosition = self.currentRowPosition[0] - 1
            if len(table._rawData) > 0:
                lastRow = len(table._rawData) - 1
                if newPosition == -1:
                    table.selectRow(lastRow)
                else:
                    table.selectRow(newPosition)

    def _populateInfoList(self, name, value):
        ''' Documentation '''

        if value is not None:
            item = QtWidgets.QListWidgetItem(name + str(value))
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # | QtCore.Qt.ItemIsEditable)
            self.listWidgetsHitDetails.addItem(item)
        else:
            value = 'Not Given'
            item = QtWidgets.QListWidgetItem(name + str(value))
            self.listWidgetsHitDetails.addItem(item)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)  # | QtCore.Qt.ItemIsEditable)

    def _showHitInfoOnDisplay(self, substance):
        ''' Documentation '''
        self._clearListWidget()
        self._showMolecule(substance)
        self._showTextHitDetails(substance)

    def _showTextHitDetails(self, substance):
        ''' Documentation '''
        if substance is not None:

            ## setSpectrum Hit
            # headerHit =  QtWidgets.QListWidgetItem('\nSpectrum Hit Details')
            # headerHit.setFlags(QtCore.Qt.NoItemFlags)
            # headerHit.setTextColor(ListWidgetHeaderColor)
            # self.listWidgetsHitDetails.addItem(headerHit)
            # for name, value in self._getSpectrumHitInfoToDisplay(substance).items():
            #   self._populateInfoList(name, value)

            ## setSubstance

            self.substanceDetailsLabel.set(ReferenceLabel + substance.name)
            headerSubstance = QtWidgets.QListWidgetItem('\nSubstance Details')
            headerSubstance.setFlags(QtCore.Qt.NoItemFlags)
            # headerSubstance.setTextColor(ListWidgetHeaderColor)
            self.listWidgetsHitDetails.addItem(headerSubstance)
            for name, value in self._getSubstanceInfoToDisplay(substance).items():
                self._populateInfoList(name, value)

            ## setSample
            if len(substance.sampleComponents) > 0:
                sampleComponent = substance.sampleComponents[0]
                if sampleComponent is not None:
                    sample = sampleComponent.sample
                    headerSample = QtWidgets.QListWidgetItem('\n' + sample.name + ' Details')
                    headerSample.setFlags(QtCore.Qt.NoItemFlags)
                    # headerSample.setTextColor(ListWidgetHeaderColor)
                    self.listWidgetsHitDetails.addItem(headerSample)
                    for name, value in self._getSampleInfoToDisplay(sample).items():
                        self._populateInfoList(name, value)

    def _showMolecule(self, substance):
        ''' Documentation '''
        if substance is not None:
            if substance.smiles is not None:
                smiles = substance.smiles
                self.compoundView.setSmiles(smiles)

    def _scoreEdit(self, hit, value):
        ''' Allows to edit the hit merit score '''
        if hit is not None:
            hit.meritCode = value

    def _updateHitTable(self):
        ''' Documentation '''
        if self.project is not None:
            self._setSpectrumHitTable()

    def _exportHitsToXlsx(self):
        ''' Export a simple xlxs file from the results '''
        dataFrame = self._createHitsDataFrame()

        fType = 'XLSX (*.xlsx)'
        dialog = FileDialog
        filePath = dialog.getSaveFileName(self, filter=fType)
        dataFrame.to_excel(filePath, sheet_name='Hits', index=False)

    def _createHitsDataFrame(self):
        # FIXME Make new
        from pandas import DataFrame

        hitDic = {}

        for hit in self.project.spectrumHits:
            referenceSubstances = []
            spectrumRefNames = []
            if hit is not None:
                for pl in hit.spectrum.peakLists:
                    if pl is not None:
                        if pl.isSimulated and pl.title == SpectrumHitPeakList:
                            for peak in pl.peaks:
                                if len(peak._linkedPeaks) > 0:
                                    linkedPeak = peak._linkedPeaks[0]
                                    if linkedPeak is not None:
                                        peak._linkedPeaks = [linkedPeak]
                                        spectrumRef = linkedPeak.peakList.spectrum
                                        substanceRef = spectrumRef.referenceSubstance
                                        if substanceRef is not None:
                                            referenceSubstances.append(substanceRef.name)
                                        spectrumRefNames.append(spectrumRef.name)
            if len(referenceSubstances) > 0:
                hitDic.update({hit.substanceName: referenceSubstances})
            else:
                hitDic.update({hit: spectrumRefNames})
        ps = DataFrame(list(hitDic.items()), columns=['Spectrum Hits', 'References'])
        return ps

    def _spectrumHitNotifierCallback(self, *kwds):
        self._spectrumHits = self.project.spectrumHits
        self._updateHitTable()

    def _closeModule(self):
        """Re-implementation of closeModule function from CcpnModule to unregister notification """
        if self._spectrumHitNotifier is not None:
            self._spectrumHitNotifier.unRegister()
        super()._closeModule()

    def close(self):
        """
        Close the table from the commandline
        """
        self._closeModule()


#
#     self.strip.viewBox.autoRange()

# project.spectrumDisplays[0].spectrumActionDict[project.spectrumDisplays[0].spectrumViews[0].spectrum._apiDataSource].setChecked(False)




class CustomPeakTableWidget(PeakListTableWidget):

    def __init__(self, parent, moduleParent, mainWindow, peakList=None, actionCallback=None, selectionCallback=None, **kwds):
        if mainWindow is not None:
            PeakListTableWidget.__init__(self, parent=parent, moduleParent=moduleParent, mainWindow=mainWindow,
                                         peakList=peakList, actionCallback=actionCallback, selectionCallback=selectionCallback, vAlign='t', **kwds)


            self._widgetScrollArea.hide()
            self.setMinimumHeight(300)
            # self.posUnitPulldownLabel.hide()
            # self.posUnitPulldown.hide()
            # self.spacer = None
            # self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))


if __name__ == '__main__':
    from ccpn.ui.gui.widgets.Application import TestApplication
    from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea


    app = TestApplication()

    win = QtWidgets.QMainWindow()

    moduleArea = CcpnModuleArea(mainWindow=None, )
    module = HitsAnalysis(mainWindow=None)
    moduleArea.addModule(module)

    win.setCentralWidget(moduleArea)
    win.resize(1000, 500)
    win.setWindowTitle('Testing %s' % module.moduleName)
    win.show()

    app.start()
