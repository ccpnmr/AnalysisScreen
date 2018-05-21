from ccpn.framework.Framework import Framework
from ccpn.core.Project import Project
from ccpn.pipes import loadedPipes
from ccpn.AnalysisScreen.pipes import _loadScreenPipes
from ccpn.AnalysisScreen.lib.ScreenLookup import _loadScreenLookupFile
from ccpn.AnalysisScreen.gui.popups.MixtureGenerationPopup import MixtureGenerationPopup
from ccpn.AnalysisScreen.gui.modules.HitAnalyis import HitsAnalysis
from ccpn.AnalysisScreen.gui.modules.MixtureAnalysis import MixtureAnalysis
from ccpn.ui.gui.widgets import MessageDialog
from ccpn.ui.gui.modules.PipelineModule import GuiPipeline
from ccpn.ui.gui.popups.PickPeaks1DPopup import PickPeak1DPopup
from ccpn.AnalysisAssign.AnalysisAssign import Assign

# applicationName = 'Screen'

_loadScreenPipes()  # load screen specific pipes

class Screen(Assign):
  """Root class for Screen application"""

  def __init__(self, applicationName, applicationVersion, commandLineArguments):
    Framework.__init__(self, applicationName, applicationVersion, commandLineArguments)


  #########################################    Start setup Menu      #############################################

  def setupMenus( self ):
    super().setupMenus( )

    menuSpec = ('Screen',[
                         # ("Pick Peaks "        , self.showPickPeakPopup),
                         ("Generate Mixtures " , self.showMixtureGenerationPopup, [('shortcut', 'cs')]),
                         ("Mixtures Analysis " , self.showMixtureAnalysis,        [('shortcut', 'st')]),
                         ("Screening Pipeline" , self.showScreeningPipeline,      [('shortcut', 'sp')]),
                         ("Hit Analysis"       , self.showHitAnalysisModule,      [('shortcut', 'ha')]),
                         ]
                )

    self.addApplicationMenuSpec(menuSpec)


  def showPickPeakPopup(self):
    if not self.project.peakLists:
      MessageDialog.showWarning('No PeakList Found','')
      return
    else:
      popup = PickPeak1DPopup(mainWindow=self.ui.mainWindow)
      popup.exec_()
      popup.raise_()


  def showMixtureGenerationPopup(self):
    """Displays Sample creation popup."""
    popup = MixtureGenerationPopup(parent=self.ui.mainWindow, mainWindow=self.ui.mainWindow)
    popup.exec_()
    popup.raise_()
    self.ui.mainWindow.pythonConsole.writeConsoleCommand("application.showSamplePopup()")
    self.project._logger.info("application.showSamplePopup()")

  def showMixtureAnalysis(self, position='bottom', relativeTo=None):
    """ Displays the Mixtures Analysis Module """
    showSa = MixtureAnalysis(mainWindow=self.ui.mainWindow)
    self.ui.mainWindow.moduleArea.addModule(showSa, position=position, relativeTo=relativeTo)
    self.ui.mainWindow.pythonConsole.writeConsoleCommand("application.showMixtureAnalysis()")
    self.project._logger.info("application.showMixtureAnalysis()")

  def showScreeningPipeline(self, position='bottom', relativeTo=None):

    guiPipeline = GuiPipeline(mainWindow=self.ui.mainWindow, pipes=loadedPipes, templates=None)
    self.ui.mainWindow.moduleArea.addModule(guiPipeline, position='bottom')
    self.ui.mainWindow.pythonConsole.writeConsoleCommand("application.showScreeningPipeline()")
    self.project._logger.info("application.showScreeningPipeline()")

  def showHitAnalysisModule(self, position='top', relativeTo= None):
    # if not self.project.spectrumHits:
    #   MessageDialog.showWarning('No Spectrum Hits Found','')
    #   return
    # else:
    self.showScreeningHits = HitsAnalysis(mainWindow=self.ui.mainWindow)
    self.ui.mainWindow.moduleArea.addModule(self.showScreeningHits, position, None)
    self.ui.mainWindow.pythonConsole.writeConsoleCommand("application.showHitAnalysisModule()")
    self.project._logger.info("application.showHitAnalysisModule()")

    #########################################    End setup Menus      #############################################