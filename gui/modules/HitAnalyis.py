#=========================================================================================
# Licence, Reference and Credits
#=========================================================================================
__copyright__ = "Copyright (C) CCPN project (http://www.ccpn.ac.uk) 2014 - 2017"
__credits__ = ("Wayne Boucher, Ed Brooksbank, Rasmus H Fogh, Luca Mureddu, Timothy J Ragan"
               "Simon P Skinner & Geerten W Vuister")
__licence__ = ("CCPN licence. See http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpnLicense for licence text")
__reference__ = ("For publications, please use reference from http://www.ccpn.ac.uk/v3-software/downloads/license"
               "or ccpnmodel.ccpncore.memops.Credits.CcpNmrReference")
#=========================================================================================
# Last code modification
#=========================================================================================
__modifiedBy__ = "$modifiedBy: Ed Brooksbank $"
__dateModified__ = "$dateModified: 2017-04-07 11:41:14 +0100 (Fri, April 07, 2017) $"
__version__ = "$Revision: 3.0.b1 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================

from PyQt4 import QtCore, QtGui
from ccpn.ui.gui.modules.CcpnModule import CcpnModule
from ccpn.ui.gui.widgets.ButtonList import ButtonList
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.CompoundView import CompoundView
from ccpn.ui.gui.widgets.Icon import Icon
from ccpn.ui.gui.widgets.CheckBox import CheckBox
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Table import ObjectTable, Column, ColumnViewSettings, ObjectTableFilter
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.modules.PeakTable import PeakListTableWidget
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.widgets.Frame import Frame

from functools import partial
from ccpn.AnalysisScreen.lib.experimentAnalysis.NewHit import REFERENCEPEAKLIST, TARGETPEAKLIST
from ccpn.core.lib.Notifiers import Notifier

Qt = QtCore.Qt
Qkeys = QtGui.QKeySequence

ListWidgetHeaderColor = QtGui.QColor('Red')

ReferenceLabel = 'Reference Details: '
ALL_ExperimentTypes = 'All'
ExperimentTypesDict =  {
                        'STD':'STD.H',
                        'Water-LOGSY':'Water-LOGSY.H',
                        'H':'H',
                        't1rho':'H[t1rho(H)]' ,
                        ALL_ExperimentTypes: None
                        }

class HitsAnalysis(CcpnModule):

  includeSettingsWidget = True
  maxSettingsState = 2
  settingsPosition = 'top'
  className = 'ScreeningHits'

  def __init__(self, mainWindow, name='Hit Analysis', **kw):
    super(HitsAnalysis, self)
    CcpnModule.__init__(self, mainWindow=mainWindow, name=name)

    self._spectrumHits = []
    self.application = None
    self.project = None
    self.current = None
    self.preferences = None

    if mainWindow is not None:
      self.mainWindow = mainWindow
      self.project = self.mainWindow.project
      self.application = self.mainWindow.application
      self.moduleArea = self.mainWindow.moduleArea
      self.preferences = self.application.preferences
      self.current = self.application.current
      self._spectrumHits = self.project.spectrumHits



    ######## ======== Icons ====== ########
    self.acceptIcon = Icon('icons/dialog-apply')
    self.rejectIcon = Icon('icons/reject')
    self.nextAndCommitIcon = Icon('icons/commitNextCopy')
    self.previousAndCommitIcon = Icon('icons/commitPrevCopy')
    self.nextIcon = Icon('icons/next')
    self.previousIcon = Icon('icons/previous')
    self.undoIcon = Icon('icons/edit-undo')
    self.removeIcon = Icon('icons/list-remove')
    self.minusIcon = Icon('icons/minus')
    self.settingIcon = Icon('icons/applications-system')
    self.exportIcon = Icon('icons/export')
    self._createWidgets()
    self._createSettingsWidgets()

    # set notifier
    if self.project is not None:
      self._spectrumHitNotifier = Notifier(self.project, [Notifier.DELETE, Notifier.CREATE, Notifier.CHANGE],
                                           'SpectrumHit', self._spectrumHitNotifierCallback)
  def _createWidgets(self):
    ''' Documentation '''

    self.mainWidget.setContentsMargins(20,20,20,20)


    ## Set ExperimentType Frame
    column = 0
    self.experimentTypeWidgetsFrame = Frame(self.mainWidget,  setLayout=True, margins=(10,10,10,10),
                                           grid=(0, column))
    column += 1
    self.spectrumHitWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10, 10, 10, 10),
                                           grid=(0, column), gridSpan=(2, column))
    self.spectrumHitWidgetsFrame.setMinimumWidth(200)
    column += 1
    self.peakHitWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10, 10, 10, 10),
                                          grid=(1, column))
    self.peakHitWidgetsFrame.setMinimumWidth(400)
    # column += 1
    self.referenceWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10, 10, 10, 10),
                                          grid=(0, column))
    self.referenceWidgetsFrame.setMinimumWidth(400)
    column += 1
    self.substanceDetailsFrame = Frame(self.mainWidget, setLayout=True, margins=(10, 10, 10, 10),
                                          grid=(0, column), gridSpan=(2, column))
    self._setExperimentTypeWidgets()
    self._setSpectrumHitWidgets()
    self._setPeakHitWidgets()
    self._setReferenceHitWidgets()
    self._setSubstanceDetailsWidgets()
    self._setSpectrumHitTable()

  def _setExperimentTypeWidgets(self):
    self.experimentTypeLabel = Label(self.experimentTypeWidgetsFrame, text='Experiment Type',
                                     grid=(0, 0), vAlign='t',)

    self.experimentTypeRadioButtons = RadioButtons(self.experimentTypeWidgetsFrame,
                                                   texts=sorted(list(ExperimentTypesDict.keys())),
                                                   callback=self._showBytExperimentType,
                                                   direction='V',
                                                   grid=(1, 0))
    self.experimentTypeWidgetsFrame.getLayout().setAlignment(Qt.AlignTop)

  def _setSpectrumHitWidgets(self):

    self.spectrumHitTableLabel = Label(self.spectrumHitWidgetsFrame, text='SpectrumHits',vAlign='t',
                               grid = (0, 0))


    self.hitTable = ObjectTable(self.spectrumHitWidgetsFrame, columns=[], actionCallback=None,
                               selectionCallback=self._selectionCallback, objects=[],
                               grid=(1, 0))


    self.hitButtons = ButtonList(self.spectrumHitWidgetsFrame, texts=['', '', '', '', ''],
                               callbacks=[partial(self._movePreviousRow,self.hitTable),
                                          self._deleteHit,
                                          partial(self._setHitIsConfirmed,False),
                                          partial(self._setHitIsConfirmed,True),
                                          partial(self._moveNextRow, self.hitTable)],
                               icons=[self.previousIcon, self.minusIcon, self.rejectIcon, self.acceptIcon,self.nextIcon],
                               tipTexts=[None, None, None, None, None],
                               direction='H', vAlign='b',
                               grid=(2, 0))




  def _setPeakHitWidgets(self):
    self.peakHitTableLabel = Label(self.peakHitWidgetsFrame, text='Target Peak Hits',vAlign='t',
                                       grid=(0, 0))

    self.targetPeakTable = CustomPeakTableWidget(self.peakHitWidgetsFrame, moduleParent=self, application=self.application,
                                       grid=(1, 0))

    self.peakButtons = ButtonList(self.peakHitWidgetsFrame, texts=['', '', '', ],
                                 callbacks=[partial(self._movePreviousRow,self.targetPeakTable),
                                            partial(self._deletePeaks,self.targetPeakTable) ,
                                            partial(self._moveNextRow,self.targetPeakTable)],
                                 icons=[self.previousIcon, self.minusIcon, self.nextIcon],
                                 tipTexts=[None, None,  None],
                                 direction='H', vAlign='b',
                                 grid=(2, 0))


  def _setReferenceHitWidgets(self):

    self.referencePeakTableLabel = Label(self.referenceWidgetsFrame, text='Matched Reference Peak', vAlign='t',
                                   grid=(0, 0))

    self.referencePeakTable = CustomPeakTableWidget(self.referenceWidgetsFrame, moduleParent=self, application=self.application,
                                 grid=(1, 0))

    # self.referenceButtons = ButtonList(self.referenceWidgetsFrame, texts=['', '', '', ],
    #                               callbacks=[partial(self._movePreviousRow,self.referencePeakTable),
    #                                         None,
    #                                          partial(self._movePreviousRow,self.referencePeakTable)],
    #                               icons=[self.previousIcon, self.rejectIcon, self.nextIcon],
    #                               tipTexts=[None, None, None],
    #                               direction='H', vAlign='b',
    #                               grid=(2, 0))


  def _setSubstanceDetailsWidgets(self):

    self.substanceDetailsLabel = Label(self.substanceDetailsFrame, text=ReferenceLabel,
                                       grid=(0, 0))
    self.compoundView = CompoundView(self.substanceDetailsFrame, preferences=self.preferences, smiles=[], #hAlign='t',vAlign='t',
                                 grid=(1, 0))

    self.listWidgetsHitDetails = ListWidget(self.substanceDetailsFrame, contextMenu=False, #hAlign='t',vAlign='t',
                                     grid=(2, 0))



  def _setSpectrumHitTable(self):
    "Sets parameters to the SpectrumHitTable."

    columns = [Column('Hit Name', lambda hit:str(hit.substanceName)),
               Column('Confirmed', lambda hit:str(hit.isConfirmed)), # setEditValue=lambda hit, value: self._testEditor(hit, value)),
               Column('Merit (Efficiency)', lambda hit:hit.figureOfMerit)] #setEditValue=lambda hit, value: self._scoreEdit(hit, value))]

    self.hitTable.setObjectsAndColumns(self._spectrumHits, columns)
    if len(self._spectrumHits) > 0:
      self.hitTable.setCurrentObject(self._spectrumHits[0])


  def _createSettingsWidgets(self):
    self.settingsWidget.setContentsMargins(20, 20, 20, 20)
    row = 0
    self.targetPeaksCheckbox = CheckBox(self.settingsWidget, text='Hide Target Peaks', checked=False,
                                           callback=partial(self._hideShowWidgetFromCheckBox,
                                                            widget=self.peakHitWidgetsFrame),
                                           grid=(row, 0))
    row += 1
    self.referencePeaksCheckbox = CheckBox(self.settingsWidget, text='Hide Reference Peaks', checked=False,
                                           callback=partial(self._hideShowWidgetFromCheckBox,
                                                            widget=self.referenceWidgetsFrame),
                                           grid=(row, 0))
    row +=1
    self.substanceDetailsCheckbox = CheckBox(self.settingsWidget, text='Hide Substance Details', checked=False,
                                           callback=partial(self._hideShowWidgetFromCheckBox,
                                                            widget= self.substanceDetailsFrame),
                                           grid=(row,0))


  def _hideShowWidgetFromCheckBox(self, widget):
    '''Specific to hide a widget from a checkbox callback  '''
    if self.sender() is not None:
      if self.sender().isChecked():
        widget.hide()
      else:
        widget.show()

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



  def _selectionTargetPeakCallback(self, peaks, *args):
    """
    set as current the selected peaks on the table and populates the reference peak Table
    """
    matchedPeak = None

    self.targetPeakTable._selectionCallback(peaks, *args) #set currentPeaks
    if peaks is not None:
      for peak in peaks:
        if peak._linkedPeak is not None:
          matchedPeak  = peak._linkedPeak
        else:
           #NB HACK until we have linkedPeak!!
          if peak.annotation is not None:
            matchedPeak = self.project.getByPid(peak.annotation)
      if matchedPeak is not None:
        self._populateReferencePeakTable(matchedPeak)



  def _referencePeakTableCallback(self, peaks, *args):
    self.referencePeakTable._selectionCallback(peaks, *args)
    if peaks is not None:
      for peak in peaks:
        if peak is not None:
          spectrum = peak.peakList.spectrum
          substance = spectrum.referenceSubstance
          if substance is not None:
            self._showHitInfoOnDisplay(substance)
          else:
            self._showSpectrumInfo(spectrum)


  def _showSpectrumInfo(self, spectrum):
    self._clearListWidget()
    self.compoundView.setSmiles('h')
    self.substanceDetailsLabel.set(ReferenceLabel + spectrum.name)
    self.listWidgetsHitDetails.clear()
    header = QtGui.QListWidgetItem('\n No Substance Details Found')
    header.setFlags(QtCore.Qt.NoItemFlags)
    header.setTextColor(ListWidgetHeaderColor)
    self.listWidgetsHitDetails.addItem(header)

  def _populateReferencePeakTable(self, peak):
    'populates the table only with matched peaks linked to the targetPeak'
    self.referencePeakTable.selectionCallback = self._referencePeakTableCallback
    if peak is not None:
      referencePeakList = peak.peakList
      self.referencePeakTable.pLwidget.select(referencePeakList.pid)
      if referencePeakList is not None:
        self.referencePeakTable._updateTable(useSelectedPeakList=False, peaks=[peak])
      self.referencePeakTable.selectObject(peak)





  def _setTargetPeakTable(self):
    self.referencePeakTable.clearTable()
    targetPeakList = self._getTargetPeakList()
    if targetPeakList is not None:
      self.targetPeakTable.pLwidget.select(targetPeakList.pid)
      self.targetPeakTable._updateTable()
      self.targetPeakTable.selectionCallback = self._selectionTargetPeakCallback
      if len(self.targetPeakTable.objects)>0:
        self.targetPeakTable.selectObject(self.targetPeakTable.objects[0])
    else:
      self.targetPeakTable.clearTable()


  def _getTargetPeakList(self):
    if self.current is not None:
      if self.current.spectrumHit is not None:
        for pl in self.current.spectrumHit.spectrum.peakLists:
          if pl.isSimulated and pl.title == TARGETPEAKLIST:
            return pl



  def _setHitIsConfirmed(self, value:bool):
    ''' Documentation '''
    if self.current is not None:
      hit = self.current.spectrumHit
      if hit is not None:
        hit.isConfirmed = value
        self._updateHitTable()

  def _selectionCallback(self, spectrumHit, *args):
    """
    set as current the selected spectrumHit on the table
    """
    if self.current is not None:
      if spectrumHit is None:
        self.current.spectrumHit = None
      else:
        self.current.spectrumHit = spectrumHit

      self._setTargetPeakTable()


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

      self._selectFirstRowHitTable()

  def _selectFirstRowHitTable(self):
    if len(self.hitTable.objects) >0:
      self.hitTable.selectObject(self.hitTable.objects[0])

  def _deletePeaks(self, table):
    if table is not None:
      peaks = table.getSelectedObjects()
      for peak in peaks:
        if peak is not None:
          peak.delete()

    self._updateHitTable()
    self.referencePeakTable.clearTable()


  def _getSampleInfoToDisplay(self, sample):
    ''' Documentation '''
    if sample is not None:
      sampleInfo = {'Name: ':sample.name,
                    'Amount: ':sample.amount,
                    'CreationDate: ':sample.creationDate,
                    'PlateIdentifier: ':sample.plateIdentifier,
                    'RowNumber: ':sample.rowNumber,
                    'ColumnNumber: ':sample.columnNumber,
                    'Comment: ':sample.comment,}
      return sampleInfo
    else:
      return {'Link to a Substance to display contents': ''}


  def _getSubstanceInfoToDisplay(self, substance):
    ''' Documentation '''
    if substance is not None:

      substanceInfo = {'name: ':substance.name,
                    'synonyms: ':substance.synonyms,
                    'userCode: ':substance.userCode,
                    'empiricalFormula: ':substance.empiricalFormula,
                    'molecularMass: ':substance.molecularMass,
                    'atomCount: ':substance.atomCount,
                    'bondCount: ':substance.bondCount,
                    'ringCount: ':substance.ringCount,
                    'hBondDonorCount: ':substance.hBondDonorCount,
                    'hBondAcceptorCount: ':substance.hBondAcceptorCount,
                    'polarSurfaceArea: ':substance.polarSurfaceArea,
                    'logPartitionCoefficien: ':substance.logPartitionCoefficient,
                    'comment: ':substance.comment}
      return substanceInfo

    else:
     return {'Link to a Substance to display contents': ''}


  def _moveNextRow(self, table):
    ''' Documentation '''

    self.currentRowPosition = table.getSelectedRows()
    if len(table.objects) > 0:
      if len(self.currentRowPosition)>0:
          newPosition = self.currentRowPosition[0]+1
          table.selectRow(newPosition)
          lastRow = len(table.objects) - 1
          if newPosition >= len(table.objects):
            table.selectRow(0)
          else:
            table.selectRow(newPosition)
      else:
        try:
          table.selectRow(0)
        except:
          pass



  def _movePreviousRow(self, table):
    ''' Documentation '''

    self.currentRowPosition = table.getSelectedRows()
    if len(self.currentRowPosition) > 0:
      newPosition = self.currentRowPosition[0]-1
      if len(table.objects)>0:
        lastRow = len(table.objects)-1
        if newPosition == -1:
          table.selectRow(lastRow)
        else:
          table.selectRow(newPosition)


  def _populateInfoList(self, name, value):
    ''' Documentation '''

    if value is not None:
      item = QtGui.QListWidgetItem(name+str(value))
      item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)# | QtCore.Qt.ItemIsEditable)
      self.listWidgetsHitDetails.addItem(item)
    else:
      value = 'Not Given'
      item = QtGui.QListWidgetItem(name+str(value))
      self.listWidgetsHitDetails.addItem(item)
      item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)# | QtCore.Qt.ItemIsEditable)



  def _showHitInfoOnDisplay(self, substance):
    ''' Documentation '''
    self._clearListWidget()
    self._showMolecule(substance)
    self._showTextHitDetails(substance)



  def _showTextHitDetails(self, substance):
    ''' Documentation '''
    if substance is not None:


      ## setSpectrum Hit
      # headerHit =  QtGui.QListWidgetItem('\nSpectrum Hit Details')
      # headerHit.setFlags(QtCore.Qt.NoItemFlags)
      # headerHit.setTextColor(ListWidgetHeaderColor)
      # self.listWidgetsHitDetails.addItem(headerHit)
      # for name, value in self._getSpectrumHitInfoToDisplay(substance).items():
      #   self._populateInfoList(name, value)

      ## setSubstance

      self.substanceDetailsLabel.set(ReferenceLabel+substance.name)
      headerSubstance =  QtGui.QListWidgetItem('\nSubstance Details')
      headerSubstance.setFlags(QtCore.Qt.NoItemFlags)
      headerSubstance.setTextColor(ListWidgetHeaderColor)
      self.listWidgetsHitDetails.addItem(headerSubstance)
      for name, value in self._getSubstanceInfoToDisplay(substance).items():
        self._populateInfoList(name, value)

      ## setSample
      if len(substance.sampleComponents)>0:
        sampleComponent = substance.sampleComponents[0]
        if sampleComponent is not None:
          sample = sampleComponent.sample
          headerSample =  QtGui.QListWidgetItem('\n'+sample.name+' Details')
          headerSample.setFlags(QtCore.Qt.NoItemFlags)
          headerSample.setTextColor(ListWidgetHeaderColor)
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
      hits = [hit for hit in self._spectrumHits if hit is not None]
      self.hitTable.setObjects(hits)
    else:
      self.hitTable.setObjects([])


  def _spectrumHitNotifierCallback(self, *kw):
    self._spectrumHits = self.project.spectrumHits
    self._updateHitTable()


  def _closeModule(self):
    """Re-implementation of closeModule function from CcpnModule to unregister notification """
    if self._spectrumHitNotifier is not None:
      self._spectrumHitNotifier.unRegister()
    super(HitsAnalysis, self)._closeModule()

  def close(self):
    """
    Close the table from the commandline
    """
    self._closeModule()
#
#     self.strip.viewBox.autoRange()

# project.spectrumDisplays[0].spectrumActionDict[project.spectrumDisplays[0].spectrumViews[0].spectrum._apiDataSource].setChecked(False)

class CustomPeakTableWidget(PeakListTableWidget):

  def __init__(self, parent, moduleParent, application, peakList=None, **kwds):

    if application is not None:
      PeakListTableWidget.__init__(self, parent=parent, moduleParent=moduleParent, application=application,
                                   peakList=peakList, updateSettingsWidgets=False, **kwds)

      self.pLwidget.hide()
      self.posUnitPulldownLabel.hide()
      self.posUnitPulldown.hide()
      # self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))



if __name__ == '__main__':
  from ccpn.ui.gui.widgets.Application import TestApplication
  from ccpn.ui.gui.widgets.CcpnModuleArea import CcpnModuleArea

  app = TestApplication()

  win = QtGui.QMainWindow()

  moduleArea = CcpnModuleArea(mainWindow=None, )
  module = HitsAnalysis(mainWindow=None)
  moduleArea.addModule(module)

  win.setCentralWidget(moduleArea)
  win.resize(1000, 500)
  win.setWindowTitle('Testing %s' % module.moduleName)
  win.show()

  app.start()