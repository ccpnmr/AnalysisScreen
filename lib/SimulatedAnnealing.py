#  Part of the Simulated Annealing algorithm is inspired by NMRmix.
#  As pubblished in J.L. Stark, et al. NMRmix: a tool for the optimization of compound mixtures in 1D (1)H NMR ligand affinity screens
#  J Proteome Res, 15 (2016), pp. 1360–1368

import math
import random
import copy
import pandas as pd
import numpy as np
import datetime
from itertools import combinations
from numba import jit
from ccpn.ui.gui.widgets.MessageDialog import _stoppableProgressBar

from ccpn.AnalysisScreen.lib.experimentAnalysis.MatchPositions import matchingPosition

def randomDictMixtures(name, compounds, nMixtures):
  mixturesDict = {}
  n,b,mixtures = len(compounds),0,[]
  compounds = list(compounds)
  compounds = random.sample(compounds, len(compounds))
  for k in range(nMixtures):
      a, b = b, b + (n+k)//nMixtures
      key = str(name)+'-'+str(k+1)
      value = compounds[a:b]
      mixturesDict.update({key:value})
  return mixturesDict

def _getScore(overlapCount, compoundPeaksCount,  scalingFactor=1):
  try:
    return (scalingFactor * (overlapCount / compoundPeaksCount))
  except ZeroDivisionError:
    return 0


def _getOverlapCount(compoundA, compoundB, minDist):
  "for refactoring"
  a, b = np.array(compoundA), np.array(compoundB)
  c = abs(b[:, None] - a)
  d = np.argwhere(c < minDist)
  overlapCount = d.shape[0]
  return overlapCount


def scoreCompound(compoundA, compoundB, minDist, scalingFactor=1):
  overlapCount = _getOverlapCount(compoundA, compoundB, minDist)
  compoundPeaksCount = len(compoundB)
  score =  _getScore(overlapCount, compoundPeaksCount,  scalingFactor)
  return score

def scoreCompound_OLD(compoundA, compoundB, minDist, scalingFactor=1):
  """ OLD slow keep for backup"""
  overlapCount = 0
  for shiftA in compoundA:
    for shiftB in compoundB:
      if abs(shiftA - shiftB) < minDist:
        overlapCount += 1
        continue
  try:
   return(scalingFactor * (overlapCount / len(compoundA)))
  except ZeroDivisionError:
    return 0

def scoreMixture_(mixture, minDist):
  "for refactoring"
  l = list(combinations(mixture, 2))
  score = np.sum([scoreCompound(i[0][1],i[1][1], minDist=minDist) for i in l])
  return score


def scoreMixture(mixture, minDist):
  score = 0
  for compoundA in mixture:
    for compoundB  in mixture:
      if compoundA[0] is not compoundB[0]:
        score += scoreCompound(compoundA[1], compoundB[1], minDist=minDist)
  return score


def calculateTotalScore(mixturesDict, peaksDistance=0.01):
  score = 0
  if mixturesDict is  None: return 0
  for mixture in mixturesDict:
    score += scoreMixture(mixturesDict[mixture], peaksDistance)
  return score


# def getAllOverlappedPositions(mixtures, minDist):
# 
#   for mixtureName, compounds in mixtures.items():
#     for compound in compounds:
#       compoundName, compoundPeakList = compound
#       compoundsToCompare = [c[1] for c in compounds if c[0] != compoundName]
#       overlaped = calculateOverlapCount(compoundPeakList, compoundsToCompare, minDist )
#       if overlaped is None:
#         print(compoundName, 'No Overlapped peaks found')
#       else:
#         score = len(overlaped) / len(compoundPeakList)
#         # print(compoundName, ' --> Counts',len(list(set(overlaped))), ' --> Overlapped positions:', overlaped, 'score: -->', score)


def getOverlappedCount(mixtureCompounds, minDist=0.01):
    "called from score single sample"
    # TODO get rid of . Duplicated routine,
    totalOverlapped  = 0
    overlaps = []
    for compound in mixtureCompounds:
      compoundName, compoundPeakList = compound
      compoundsToCompare = [c[1] for c in mixtureCompounds if c[0] != compoundName]
      overlaped = calculateOverlapCount(compoundPeakList, compoundsToCompare, minDist)
      if overlaped is None:
        # print(compoundName, 'No Overlapped peaks found')
        continue
      else:
        totalOverlapped += len(list(set(overlaped)))
        overlaps.append(list(set(overlaped)))
        # print('Component %s, overlaps at positions: %s ' %(compoundName, list(set(overlaped))))
    totalOverlapped = len(list(set([o for j in overlaps for o in j])))
    # print('Total Overlaps for Mixture ', totalOverlapped)
    return totalOverlapped

def calculateOverlapCount(compoundA, mixture, minimalOverlap):
  "called from score single sampleComponent and sample"
  # TODO get rid of . Duplicated routine,
  ll = []
  for compound in mixture:
    overlaped = [peakA for peak in compound for peakA in compoundA if abs(peak - peakA) <= minimalOverlap]
    if len(overlaped)>0:
      ll.append(overlaped)
      # return overlaped
  return [j for l in ll for j in l]



def findBestMixtures(mixturesSteps):
  bestMixturesStep = list(mixturesSteps.items())
  if len(bestMixturesStep) > 0:
    bestMixtures = min(bestMixturesStep)[1]
    return bestMixtures

def mixTwoMixturesDict(mixtures):
  mixturesList = list(mixtures.items())
  sampledMixtures = random.sample(mixturesList, 2)
  mixturesToMix = dict(sampledMixtures)
  swaps = []
  for i, mixture in enumerate(list(mixturesToMix.values())):
    randInt = random.randint(0, len((mixture)[i]) - 1)
    pick = list(mixturesToMix.values())[i][randInt]
    list(mixturesToMix.values())[i].remove(pick)
    swaps.append(pick)
  for i, mixture in enumerate(list(mixturesToMix.values())):
    pick = swaps.pop()
    list(mixturesToMix.values())[i].append(pick)
  for m in sampledMixtures:
    mixturesList.remove(m)
  mixedMixtures = mixturesList + list(mixturesToMix.items())
  return dict(mixedMixtures)

@jit(nopython=True)
def getLinearSteps(startTemp=1000.0, finalTemp = 0.1, maxSteps = 1000):
  tSteps = (startTemp - finalTemp) / maxSteps  # 1)
  temp = startTemp
  while True:
    yield temp
    temp -= tSteps

@jit(nopython=True)
def getExponentialSteps(startTemp=1000.0, finalTemp = 0.1, maxSteps = 100):
  aTemp = math.exp((math.log(finalTemp / startTemp)) / maxSteps)
  temp = startTemp
  while True:
    yield temp
    temp *=  aTemp

def runCooling(type, startTemp=1000.0, finalTemp = 0.1, maxSteps = 1000):
  if type == 'exponential':
    coolingSchedule = getExponentialSteps(startTemp, finalTemp, maxSteps)
  elif type == 'Linear':
    coolingSchedule = getLinearSteps(startTemp, finalTemp, maxSteps)
  else:
    print('Cooling type not implemented yet, Used linear instead')
    coolingSchedule = getLinearSteps()
  return coolingSchedule

@jit(nopython=True)
def getProbability(scoreDiff, currentTemp, tempK):
  if currentTemp == 0:
    return 0
  k = tempK
  probabilty = math.exp(-(scoreDiff)*k / ( currentTemp))
  return probabilty


from tqdm import tqdm


def annealling(mixtures, coolingMethod='Linear', startTemp=1000, finalTemp=0.01,
               maxSteps=1000, tempK=200, minDistance=0.01):
  mixturesSteps = {}
  coolingSchedule = runCooling(coolingMethod, startTemp, finalTemp, maxSteps)
  currScore = calculateTotalScore(mixtures,minDistance)
  scores = []
  probabilities  = []
  step = 1
  for currentTemp in tqdm(coolingSchedule):
    newMixtures = mixTwoMixturesDict(mixtures)
    copyNewMixtures = copy.deepcopy(newMixtures)
    newScore = calculateTotalScore(newMixtures,minDistance)
    # print('Annealing .... : T%s, Score %s' %(currentTemp, newScore,) )
    scoreDiff = abs(newScore - currScore)
    scores.append(newScore)
    if newScore == 0:
      return copyNewMixtures
    elif newScore <= currScore:
      mixtures = newMixtures
      currScore = newScore
      mixturesSteps.update({newScore: copyNewMixtures})
    else:
      probability = getProbability(scoreDiff,currentTemp, tempK)
      probabilities.append(probability)
      if random.random() < probability:
        mixtures = newMixtures
        currScore = newScore
        mixturesSteps.update({newScore: copyNewMixtures})

    step += 1
    if step > maxSteps:
      break
  if len(scores)>0:
    bestScore = min(scores)
    # print('--> bestScore anniling:',bestScore)
  bestMixtures = findBestMixtures(mixturesSteps)
  return  bestMixtures

def iterateAnnealing(mixtures, startTemp=1000, finalTemp=0.01, maxSteps=1000, tempK=200, coolingMethod='linear',
                     nIterations=1, minDistance=0.01, minTotalScore = None):
  print('Starting Annealing Iterations ')
  totalScores = []
  bestIteration = {} #score:mixture
  startingScore = calculateTotalScore(mixtures, minDistance)
  bestIteration.update({startingScore: mixtures})
  if minTotalScore is None:
    minTotalScore = startingScore
  # print('startingScore', startingScore)
  copyMixtures = copy.deepcopy(mixtures)
  if startingScore == 0:
    return mixtures
  i = 0
  # while  i <= nIterations:
  # for i in range(0,nIterations):
  newMixtures = annealling(mixtures, coolingMethod=coolingMethod, startTemp=startTemp, finalTemp=finalTemp,
                           maxSteps=maxSteps, tempK=tempK, minDistance=minDistance)
  copyNewMixtures = copy.deepcopy(newMixtures)
  if newMixtures:
    currScore = calculateTotalScore(newMixtures,minDistance)
    bestIteration.update({currScore: newMixtures})
    totalScores.append(currScore)
    if currScore == 0:
      return copyNewMixtures
    j = 0
    while currScore >= startingScore or j <= nIterations:
      print('Iteration...:',j)
      if j == nIterations:
        print('Reached max n of iterations...', j)
        break
      newMixtures = annealling(mixtures, coolingMethod=coolingMethod, startTemp=startTemp, finalTemp=finalTemp,
                               maxSteps=maxSteps, tempK=tempK, minDistance=minDistance)
      currScore = calculateTotalScore(newMixtures, minDistance)
      totalScores.append(currScore)
      if currScore <= startingScore:
        print('Iteration: %s . Current score: %s. Starting Score: %s ' %(j, currScore, startingScore))
        bestIteration.update({currScore: newMixtures})
        startingScore = currScore
      j += 1
    print('currScore %s, minTotalScore: %s, j: %s, nIterations:%s '%(currScore, minTotalScore, j, nIterations))

  df = pd.DataFrame(totalScores)
  dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(' ','_')
  # df.to_excel('/Users/luca/Desktop/PhD/data/UCB/results/mixtures/allScores__'+dt+'.xlsx')
  if len(bestIteration)>0:
    print("Annealing Finished")
    bestMixtures = findBestMixtures(bestIteration)
    return bestMixtures
  else:
    print('No Better Iteration found, original mixtures are returned')
    # sc = calculateTotalScore(copyMixtures, minDistance)
    return copyMixtures


def _showScoresPerMixture(mixtures, minDistance):
  scoring = []
  for mixtureName, mixCompounds in mixtures.items():
    scoring.append(str(mixtureName)+ '  score: ' + str(scoreMixture(mixCompounds, minDistance)))
  return scoring


def greedyMixtures(compounds, maxSize, minDistance, maxPeaksOverlapped=None):
  mixtures = [[]] * len(compounds)
  for compound in compounds:
    compoundMixtured = False
    mixtureCount = 0
    while not compoundMixtured:
      if len(mixtures[mixtureCount]) < maxSize:
        mixtureScore = scoreMixture(mixtures[mixtureCount], minDistance)
        trialMixture = mixtures[mixtureCount] + [compound, ]
        if scoreMixture(trialMixture, minDistance) == mixtureScore:
          mixtures[mixtureCount] = trialMixture
          compoundMixtured = True
      mixtureCount += 1
  return [mixture for mixture in mixtures if len(mixture)>0]



############

# Not used. to be removed
# def _calculateSingleCompoundScore(compoundA, mixture, minimalOverlap):
#   for mix, compounds in mixture.items():
#     for compound in compounds:
#       overlaped = [peakA for peak in compound[1] for peakA in compoundA[1] if abs(peak - peakA) <= minimalOverlap]
#       scoring = len(overlaped) / len(compoundA[1])

# def getMixtureInfo(mixture, minDist):
#
#   for compound in mixture:
#     compoundName, compoundPeakList = compound
#     compoundsToCompare = [c[1] for c in mixture if c[0] != compoundName]
#     overlaped = calculateOverlapCount(compoundPeakList, compoundsToCompare, minDist )
#
#     if overlaped is None:
#       print(compoundName, 'No Overlapped peaks found')
#     else:
#       score = len(overlaped) / len(compoundPeakList)
#       print(compoundName, ' --> Counts',len(list(set(overlaped))), ' --> Overlapped positions:', overlaped, 'score: -->', score)

# def getAllOverlappedPositions(mixtures, minDist):
#
#   for mixtureName, compounds in mixtures.items():
#     for compound in compounds:
#       compoundName, compoundPeakList = compound
#       compoundsToCompare = [c[1] for c in compounds if c[0] != compoundName]
#       overlaped = calculateOverlapCount(compoundPeakList, compoundsToCompare, minDist )
#       if overlaped is None:
#         print(compoundName, 'No Overlapped peaks found')
#       else:
#         score = len(overlaped) / len(compoundPeakList)
#         # print(compoundName, ' --> Counts',len(list(set(overlaped))), ' --> Overlapped positions:', overlaped, 'score: -->', score)
#
# def generateSimpleCompounds(numb, numberOfPeaks, ppmStart, ppmEnd):
#   compounds = []
#   for i in range(numb):
#     compound = generatePeakPositions(numberOfPeaks, ppmStart, ppmEnd)
#     compounds.append(compound)
#   return compounds

# def generatePeakPositions(numberOfPeaks, ppmStart, ppmEnd):
#   peakPositions = []
#   for x in range(numberOfPeaks):
#     peakPositions.append(random.uniform(ppmStart, ppmEnd))
#   return sorted(peakPositions)