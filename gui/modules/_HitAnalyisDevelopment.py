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
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.Table import ObjectTable, Column
from ccpn.ui.gui.widgets.ListWidget import ListWidget
from ccpn.ui.gui.modules.PeakTable import PeakListTableWidget
from ccpn.ui.gui.widgets.RadioButtons import RadioButtons
from ccpn.ui.gui.widgets.Frame import Frame

Qt = QtCore.Qt
Qkeys = QtGui.QKeySequence

class HitsAnalysis(CcpnModule):

  includeSettingsWidget = False
  maxSettingsState = 2
  settingsPosition = 'top'
  className = 'ScreeningHits'

  def __init__(self, mainWindow, name='Hit Analysis', **kw):
    super(HitsAnalysis, self)
    CcpnModule.__init__(self, mainWindow=mainWindow, name=name)

    self._spectrumHits = []

    self.application = None
    self.project = None

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


  def _createWidgets(self):
    ''' Documentation '''

    self.mainWidget.setContentsMargins(20,20,20,20)


    ## Set ExperimentType Frame
    column = 0
    self.experimentTypeWidgetsFrame = Frame(self.mainWidget,  setLayout=True, margins=(10,10,10,10),
                                         grid=(0, column))

    self.experimentTypeLabel = Label(self.experimentTypeWidgetsFrame, text='Experiment Type',
                                     grid=(0, 0), vAlign='t',)

    self.experimentTypeRadioButtons = RadioButtons(self.experimentTypeWidgetsFrame,
                                                   texts=['1H', 'STD', 'WaterLogsy', 't1'],
                                                   direction='V',
                                                   grid=(1, 0))
    self.experimentTypeWidgetsFrame.getLayout().setAlignment(Qt.AlignTop)


    ## Set SpectrumHit Table Label
    column += 1
    self.spectrumHitWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10,10,10,10),
                                     grid=(0, column))
    self.spectrumHitTableLabel = Label(self.spectrumHitWidgetsFrame, text='SpectrumHits',vAlign='t',
                               grid = (0, 0))

    ## Set SpectrumHit Table
    self.hitTable = ObjectTable(self.spectrumHitWidgetsFrame, columns=[], actionCallback=self._hitTableCallback,
                               selectionCallback=self._selectionCallback, objects=[],
                               grid=(1, 0))
    self._setSpectrumHitTable()

    ## Set SpectrumHit Table Buttons
    self.hitButtons = ButtonList(self.spectrumHitWidgetsFrame, texts=['', '', '', '', ''],
                               callbacks=[self._movePreviousRow, self._deleteHit, self._rejectAssignment,
                                          self._acceptAssignment, self._moveNextRow],
                               icons=[self.previousIcon, self.minusIcon, self.rejectIcon, self.acceptIcon,self.nextIcon],
                               tipTexts=[None, None, None, None, None],
                               direction='H', hAlign='c',
                               grid=(2, 0))


    ## Set PeakHit Frame
    column += 1
    self.peakHitWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10,10,10,10),
                                       grid=(0, column))

    self.peakHitTableLabel = Label(self.peakHitWidgetsFrame, text='Target Peak Hits',vAlign='t',
                                       grid=(0, 0))

    self.peakTable = ObjectTable(self.peakHitWidgetsFrame, columns=[], actionCallback=self._hitTableCallback,
                                selectionCallback=self._selectionCallback, objects=[],
                                grid=(1, 0))

    self.peakButtons = ButtonList(self.peakHitWidgetsFrame, texts=['', '', '', ],
                                 callbacks=[self._movePreviousRow, None, self._moveNextRow],
                                 icons=[self.previousIcon, self.minusIcon, self.nextIcon],
                                 tipTexts=[None, None,  None],
                                 direction='H', hAlign='c',
                                 grid=(2, 0))


    ## Set reference Widgets frame
    column += 1
    self.referenceWidgetsFrame = Frame(self.mainWidget, setLayout=True, margins=(10,10,10,10),
                                       grid=(0, column))

    self.referencePeakTableLabel = Label(self.referenceWidgetsFrame, text='Matched Reference Peak',
                                   grid=(0, 0))

    self.referencePeakTable = ObjectTable(self.referenceWidgetsFrame, columns=[], actionCallback=self._hitTableCallback,
                                 selectionCallback=self._selectionCallback, objects=[],
                                 grid=(1, 0))

    self.referenceButtons = ButtonList(self.referenceWidgetsFrame, texts=['', '', '', ],
                                  callbacks=[self._movePreviousRow, None, self._moveNextRow],
                                  icons=[self.previousIcon, self.minusIcon, self.nextIcon],
                                  tipTexts=[None, None, None],
                                  direction='H', hAlign='c',
                                  grid=(2, 0))

    ## Set substance Details
    column += 1
    self.substanceDetailsFrame = Frame(self.mainWidget, setLayout=True, margins=(10,10,10,10),
                                       grid=(0, column))


    self.substanceDetailsLabel = Label(self.substanceDetailsFrame, text='Substance Details',
                                       grid=(0, 0))


    self.compoundView = CompoundView(self.substanceDetailsFrame, smiles=[], #hAlign='t',vAlign='t',
                                 grid=(1, 0))
    # self.compoundView.setContentsMargins(10, 10, 10, 10)

    self.listWidgetsHitDetails = ListWidget(self.substanceDetailsFrame, #hAlign='t',vAlign='t',
                                     grid=(2, 0))

    # self.listWidgetsHitDetails.setContentsMargins(10,10,10,10)

  def _setSpectrumHitTable(self):
    "Sets parameters to the SpectrumHitTable."
    columns = [Column('Hit Name', lambda hit:str(hit.substanceName)),
               Column('Confirmed', lambda hit:str(hit.isConfirmed)), # setEditValue=lambda hit, value: self._testEditor(hit, value)),
               Column('Merit', lambda hit:str(hit.meritCode), setEditValue=lambda hit, value: self._scoreEdit(hit, value))]

    self.hitTable.setObjectsAndColumns(self._spectrumHits, columns)
    if len(self._spectrumHits) > 0:
      self.hitTable.setCurrentObject(self._spectrumHits[0])

  def _acceptAssignment(self):
    ''' Documentation '''
    hit = self.current.spectrumHit
    if hit is not None:
      hit.isConfirmed = True
      self._updateHitTable()

  def _addHit(self):
    ''' Documentation '''
    pass



  def _selectionCallback(self, spectrumHit, *args):
    """
    set as current the selected spectrumHit on the table
    """
    if spectrumHit is None:
      self.current.clearSpectrumHits()
    else:
      self.current.spectrumHit = spectrumHit


  def _clearDisplayView(self):
    ''' Documentation '''
    pass
    # # currentDisplayed = self.project.getByPid('GD:user.View.1D:H')
    #
    # currentDisplayed = self.project.strips[0]
    # for spectrumView in currentDisplayed.spectrumViews:
    #   spectrumView.delete()
    #
    # if len(self.project.windows) > 0:
    #   self.mainWindow = self.project.windows[0]
    #   self.mainWindow.clearMarks()
    # return currentDisplayed

  def _clearListWidget(self):
    ''' Documentation '''

    self.listWidgetsHitDetails.clear()

  def _commitMoveNextRow(self):
    ''' Documentation '''

    self._acceptAssignment()
    self._moveNextRow()

  def _commitMovePreviousRow(self):
    ''' Documentation '''

    self._acceptAssignment()
    self._movePreviousRow()

  def _createDummyHits(self):
    ''' Testing only '''


    self.samples = self.project.samples
    for sample in self.project.samples:
      self.substance = sample.sampleComponents[0].substance
      self.hit = sample.spectra[0].newSpectrumHit(substanceName=str(self.substance.name))
      self.hit.comment = 'No'
    # return self.project.spectrumHits

  def _deleteHit(self):
    ''' Deletes hit from project and from the table. If is last cleans all graphics
    '''
    hitToDelete = self.pullDownHit.getObject()
    hitToDelete.delete()
    if hitToDelete in self._spectrumHits:
      self._spectrumHits.remove(hitToDelete)
    self._moveNextRow()
    self._updateHitTable()
    if len(self._spectrumHits)<=0:
      self._clearDisplayView()
      self.pullDownHit.setData([])

  def _displayAllSampleComponents(self):
    ''' Documentation '''

    sampleComponentSpectra = [sc.substance.referenceSpectra[0] for sc in self.pullDownHit.currentObject().sample.sampleComponents]
    for spectrum in sampleComponentSpectra:
      spectrum.scale = float(0.5)
      # self.project.getByPid('GD:user.View.1D:H').displaySpectrum(spectrum)
      self.project.strips[0].displaySpectrum(spectrum)

  def _displaySampleAndHit(self):
    ''' Documentation '''

    currentDisplay = self._clearDisplayView()
    for spectrum in self._spectraToDisplay():
      currentDisplay.displaySpectrum(spectrum)
      # currentDisplay.showPeaks(spectrum.peakList)
    # self.project.strips[0].viewBox.autoRange()

  def _displaySelectedComponent(self):
    ''' Documentation '''

    currentDisplayed = self.project.strips[0]._parent
    for spectrumView in currentDisplayed.spectrumViews:
      if spectrumView.spectrum in self._spectraToDisplay():
        currentDisplayed.spectrumActionDict[spectrumView.spectrum._apiDataSource].setChecked(True)
      else:
        currentDisplayed.spectrumActionDict[spectrumView.spectrum._apiDataSource].setChecked(False)
    self._showHitInfoOnDisplay()


  def _getPositionOnSpectrum(self):
    ''' Documentation '''
    peaks = self._getPullDownObj().substance.referenceSpectra[0].peakLists[1].peaks
    positions = [peak.position for peak in peaks]
    return set(list(positions))


  def _getPullDownObj(self):
    ''' Documentation '''

    currentObjPulldown = self.pullDownHit.currentObject()
    if hasattr(currentObjPulldown, 'spectrum'):
      spectrumHit = currentObjPulldown
      substanceName = spectrumHit.substanceName
      substance = self.project.getByPid('SU:'+substanceName+'.')
      if substance is not None:
        return substance.sampleComponents[0]
    else:
      sampleComponent = currentObjPulldown
      return sampleComponent


  def _getSampleInfoToDisplay(self):
    ''' Documentation '''

    sample = self._getPullDownObj().sample
    sampleInfo = {'Name':sample.name,
                  'Amount':sample.amount,
                  'CreationDate':sample.creationDate,
                  'PlateIdentifier':sample.plateIdentifier,
                  'RowNumber':sample.rowNumber,
                  'ColumnNumber':sample.columnNumber,
                  'Comment':sample.comment,}
    return sampleInfo


  def _getSubstanceInfoToDisplay(self):
    ''' Documentation '''

    sampleComponent = self._getPullDownObj()
    substance = sampleComponent.substance
    substanceInfo = {'name  ':substance.name,
                  # 'synonyms ':substance.synonyms,
                  'userCode ':substance.userCode,
                  'empiricalFormula ':substance.empiricalFormula,
                  'molecularMass  ':substance.molecularMass,
                  'atomCount  ':substance.atomCount,
                  'bondCount  ':substance.bondCount,
                  'ringCount  ':substance.ringCount,
                  'hBondDonorCount  ':substance.hBondDonorCount,
                  'hBondAcceptorCount ':substance.hBondAcceptorCount,
                  'polarSurfaceArea ':substance.polarSurfaceArea,
                  'logPartitionCoefficien ':substance.logPartitionCoefficient,
                  'comment  ':substance.comment}
    return substanceInfo


  def _getSpectrumHitInfoToDisplay(self):
    ''' Documentation '''

    if len(self._getPullDownObj().spectrumHits)>0:
      hit = self._getPullDownObj().spectrumHits[0]
      hitInfo = {'Score  ':hit.figureOfMerit,
                    'Std  ':hit.meritCode,
                    'NormalisedChange ':hit.normalisedChange,
                    'concentration  ':hit.concentration,
                    'concentrationError ':hit.concentrationError,
                    'comment  ':hit.comment,
                    }
      return hitInfo
    else:
      return {'Add new hit to display contents': ''}


  def _getSelectedSample(self):
    ''' Documentation '''

    return self._getPullDownObj().sample


  def _hideDeleteButton(self):
    ''' Documentation '''

    self.showDeleteHitButtons.hide()
    self.addHitButton.show()


  def _hitTableCallback(self, row:int=None, col:int=None, obj:object=None):
    ''' Documentation '''

    pass
    # FIXME TODO
    # peaks = self._getPullDownObj().substance.referenceSpectra[0].peakLists[1].peaks
    # from ccpn.ui.gui.lib.Strip import navigateToPositionInStrip
    # if self._current.strip is not None:
    #   navigateToPositionInStrip(strip=self._current.strip, positions=peak.position)
    # for peak in peaks:
    #   navigateToPeakPosition(self.project, peak=peak, selectedDisplays=[displayed.pid], markPositions=True)


  def _moveNextRow(self):
    ''' Documentation '''

    self.currentRowPosition = self.hitTable.getSelectedRows()
    newPosition = self.currentRowPosition[0]+1
    self.hitTable.selectRow(newPosition)
    lastRow = len(self.project.spectrumHits)
    if newPosition == lastRow:
     self.hitTable.selectRow(0)


  def _movePreviousRow(self):
    ''' Documentation '''

    self.currentRowPosition = self.hitTable.getSelectedRows()
    newPosition = self.currentRowPosition[0]-1
    lastRow = len(self.project.spectrumHits)-1
    if newPosition == -1:
      self.hitTable.selectRow(lastRow)
    else:
      self.hitTable.selectRow(newPosition)


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


  def _rejectAssignment(self):
    ''' Documentation '''
    pass
    # self._updateHitTable()



  def _showHitInfoOnDisplay(self):
    ''' Documentation '''
    self._clearListWidget()
    self._showMolecule()
    self._showTextHitDetails()



  def _showTextHitDetails(self):
    ''' Documentation '''

    color = QtGui.QColor('Red')
    ''' setSpectrum Hit '''
    headerHit =  QtGui.QListWidgetItem('\nSpectrum Hit Details')
    headerHit.setFlags(QtCore.Qt.NoItemFlags)
    headerHit.setTextColor(color)
    self.listWidgetsHitDetails.addItem(headerHit)
    for name, value in self._getSpectrumHitInfoToDisplay().items():
      self._populateInfoList(name, value)

    ''' setSubstance '''
    headerSubstance =  QtGui.QListWidgetItem('\nSubstance Details')
    headerSubstance.setFlags(QtCore.Qt.NoItemFlags)
    headerSubstance.setTextColor(color)
    self.listWidgetsHitDetails.addItem(headerSubstance)
    for name, value in self._getSubstanceInfoToDisplay().items():
      self._populateInfoList(name, value)

    ''' setSample '''
    headerSample =  QtGui.QListWidgetItem('\nSample Details')
    headerSample.setFlags(QtCore.Qt.NoItemFlags)
    headerSample.setTextColor(color)
    self.listWidgetsHitDetails.addItem(headerSample)
    for name, value in self._getSampleInfoToDisplay().items():
      self._populateInfoList(name, value)

  def _showMolecule(self):
    ''' Documentation '''
    substance = self._getPullDownObj().substance
    self.smiles = substance.smiles
    if self.smiles is not None:
      self.compoundView  = CompoundView(self, smiles=self.smiles, preferences=self.preferences)
      self.hitDetailsGroupLayout.addWidget(self.compoundView, 1,1)
      self.compoundView.centerView()
      self.compoundView.resetView()
      self.compoundView.updateAll()




  def _spectraToDisplay(self):
    ''' return sample spectra and spectrum from the hit pulldown'''
    spectraToDisplay = []

    sampleSpectraToDisplay = [x for x in self.pullDownHit.currentObject().sample.spectra if x.experimentType != 'Water-LOGSY.H']

    sampleSpectraToDisplay[-1].scale =  float(0.03125)

    spectraToDisplay.append(sampleSpectraToDisplay)
    currentObjPulldown = self.pullDownHit.currentObject()

    if hasattr(currentObjPulldown, 'spectrum'):
      substanceName = currentObjPulldown.substanceName
      substanceRefSpectrum = self.project.getByPid('SU:'+str(substanceName)+'.').referenceSpectra[0]
      substanceRefSpectrum.scale = float(0.5)
      spectraToDisplay[0].append(substanceRefSpectrum)
    else:
      refSpectrum = currentObjPulldown.substance.referenceSpectra[0]
      refSpectrum.scale = float(0.5)
      spectraToDisplay[0].append(refSpectrum)
    # spectraToDisplayPL = [spectrum.peakLists[0] for spectrum in spectraToDisplay[0]]

    return spectraToDisplay[0]

  def _testEditor(self, hit, value):
    ''' Documentation '''
    hit.comment = value

  def _scoreEdit(self, hit, value):
    ''' Documentation '''
    hit.meritCode = value

  def _updateHitTable(self):
    ''' Documentation '''
    self.hitTable.setObjects(self._spectrumHits)



#   def exportToXls(self):
#     ''' Export a simple xlxs file from the results '''
#     self.nameAndPath = ''
#     fType = 'XLS (*.xlsx)'
#     dialog = FileDialog(self, fileMode=0, acceptMode=1, preferences=self.preferences, filter=fType)
#     filePath = dialog.selectedFiles()[0]
#     self.nameAndPath = filePath
#
#     sampleColumn = [str(sample.pid) for sample in self.project.samples]
#     sampleHits = [str(sample.spectrumHits) for sample in self.project.samples]
#     df = DataFrame({'Mixture name': sampleColumn, 'Sample Hits': sampleHits})
#     df.to_excel(self.nameAndPath, sheet_name='sheet1', index=False)


#
#     self.strip.viewBox.autoRange()

# project.spectrumDisplays[0].spectrumActionDict[project.spectrumDisplays[0].spectrumViews[0].spectrum._apiDataSource].setChecked(False)


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