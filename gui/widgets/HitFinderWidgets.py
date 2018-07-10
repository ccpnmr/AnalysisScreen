from functools import partial
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.PulldownList import PulldownList
from ccpn.ui.gui.widgets.CheckBox import CheckBox

def _disableReferenceSG(cls, referenceSpectrumGroup):
  pulldown = getattr(cls, referenceSpectrumGroup)
  checkBox  = cls.sender()
  if pulldown is not None and checkBox is not None:
    if checkBox.isChecked():
      pulldown.setData([])
      pulldown.setEnabled(False)
    else:
      if cls is not None:
        if cls.spectrumGroups is not None:
          data = [sg.pid for sg in cls.spectrumGroups]
          if len(data)>0:
            pulldown.setData(data)
          else:
            pulldown.setData(texts=[cls._pulldownSGHeaderText],
                             icons=[cls._warningIcon])

      pulldown.setEnabled(True)

def _addSGpulldowns(cls, row, SGVarNames):
  for varName in SGVarNames:
    label = Label(cls.pipeFrame, varName, grid=(row, 0))
    setattr(cls, varName, PulldownList(cls.pipeFrame, headerText=cls._pulldownSGHeaderText,
                                        headerIcon=cls._warningIcon, grid=(row, 1)))
    row += 1


def _addCommonHitFinderWidgets(cls, row, ReferenceSpectrumGroup, ReferenceFromMixture, MatchPeaksWithin,
                               DefaultMinDist, thresholdName, defaultThreshold):

  isMixtureLabel = Label(cls.pipeFrame, ReferenceFromMixture, grid=(row, 0))
  setattr(cls, ReferenceFromMixture, CheckBox(cls.pipeFrame, checked=False,
                                              callback=partial(_disableReferenceSG, cls, ReferenceSpectrumGroup
                                                               ),
                                              grid=(row, 1)))

  row += 1
  minimumDistanceLabel = Label(cls.pipeFrame, MatchPeaksWithin, grid=(row, 0))
  setattr(cls, MatchPeaksWithin, DoubleSpinbox(cls.pipeFrame, value=DefaultMinDist,
                                               step=DefaultMinDist, min=0.01, decimals=3, grid=(row, 1)))

  row += 1
  mEfLabel = Label(cls.pipeFrame, thresholdName, grid=(row, 0))
  setattr(cls, thresholdName, DoubleSpinbox(cls.pipeFrame, value=defaultThreshold, grid=(row, 1)))