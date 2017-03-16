__author__ = 'TJ'

from ccpn.framework import Framework
from ccpn.AnalysisScreen.AnalysisScreen import Screen as Application
from ccpn.framework.Version import applicationVersion

if __name__ == '__main__':
  from ccpn.util.GitTools import getAllRepositoriesGitCommit
  applicationVersion = 'development: {AnalysisScreen:.8s}'.format(**getAllRepositoriesGitCommit())

  # argument parser
  parser = Framework.defineProgramArguments()

  # add any additional commandline argument here
  commandLineArguments = parser.parse_args()

  application = Application('AnalysisScreen', applicationVersion, commandLineArguments)
  Framework._getApplication = lambda: application
  application.start()

