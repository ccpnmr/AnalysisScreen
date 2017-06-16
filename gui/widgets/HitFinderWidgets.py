
from ccpn.ui.gui.widgets.Label import Label
from ccpn.ui.gui.widgets.DoubleSpinbox import DoubleSpinbox
from ccpn.ui.gui.widgets.Spinbox import Spinbox
from ccpn.ui.gui.widgets.PulldownList import PulldownList


def _addSGpulldowns(cls, row, SGVarNames):
  for varName in SGVarNames:
    label = Label(cls.pipeFrame, varName, grid=(row, 0))
    setattr(cls, varName, PulldownList(cls.pipeFrame, headerText=cls._pulldownSGHeaderText,
                                        headerIcon=cls._warningIcon, grid=(row, 1)))
    row += 1


def _addCommonHitFinderWidgets(cls, row, RefPL, MatchPeaksWithin, DefaultMinDist, thresholdName, defaultThreshold):

  peakListLabel = Label(cls.pipeFrame, RefPL, grid=(row, 0))
  setattr(cls, RefPL, Spinbox(cls.pipeFrame, value=0, max=0, grid=(row, 1)))

  row += 1
  minimumDistanceLabel = Label(cls.pipeFrame, MatchPeaksWithin, grid=(row, 0))
  setattr(cls, MatchPeaksWithin, DoubleSpinbox(cls.pipeFrame, value=DefaultMinDist,
                                               step=DefaultMinDist, min=0.01, grid=(row, 1)))

  row += 1
  mEfLabel = Label(cls.pipeFrame, thresholdName, grid=(row, 0))
  setattr(cls, thresholdName, DoubleSpinbox(cls.pipeFrame, value=defaultThreshold, grid=(row, 1)))