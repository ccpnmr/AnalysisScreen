

'''
Create a new Pandas dataFrame from SpectrumHits obtained from a pipeline
'''

import pandas as pd
from ccpn.core.SpectrumHit import _getReferenceLevel, scoreHit, _norm, _grade, _scoreHits

import collections
from ccpn.core.PeakList import estimateNoiseLevel1D, estimateSNR_1D
from sklearn.preprocessing import minmax_scale
import numpy as np
# Naming
Pid = 'Pid'
ReferenceName = 'Reference'                      # -> Str | name of the spectrum used as reference
SpectrumHitName = 'SpectrumHit'                  # -> Str | name of the spectrum used to identified the hits. Like STDs of sample with target
SpectrumHitPid = SpectrumHitName+'_'+Pid
ReferencePid = ReferenceName+'_'+Pid

SampleName = 'Sample'                            # -> Str | name of the sample
ExperimentTypeName = 'ExperimentType'            # -> Str | name of ccpn ExperimentType

# Scoring
RelativeScore = 'Relative Score'                          # -> Float | relative score per each reference spectrum identified as hit.
NormalisedScore = 'Normalised Score'                      # -> Float | relative score per each reference spectrum identified as hit.
Grade =            'Grade'                                # -> Str   | conversion 0-1 to a grade scale  weak-strong
ReferenceTotalScore = 'Total Score'                       # -> Float | tot score per each reference spectrum identified as hit.
ReferenceFigureOfMerit = 'FigureOfMerit'                  # -> Float | score like efficiency for each reference
ReferenceTotalPeaksCount = 'Peaks'                        # -> Int   | tot count of peak per each reference spectrum identified as hit.
ReferenceLevel = 'Level'                                  # -> Int   | the hit level based on  how many experiment type the reference has appeared to be a hit.
OtherExpHits = 'Others'                                   # -> str   | Other experiment types the reference has appeared to be a hit.
SNR = 'SNR'
MatchesScore = 'Matches Score'                            # -> Float | score  each reference to the hit

# Peak hits positions
ReferencePeakPositions = 'PeakPositions'                 # -> list of tuple
DeltaPositions = 'DeltaPositions'                        # -> Delta positions between reference peak and target peak


Default_DataFrame = collections.OrderedDict((
                                            (ReferenceName               ,''),
                                            (SpectrumHitName             ,''),
                                            (SampleName                  ,''),
                                            (ExperimentTypeName          ,''),
                                            (SNR                         ,None),
                                            # (ReferenceFigureOfMerit      ,None),
                                            (ReferenceTotalPeaksCount    ,None),
                                            (ReferenceLevel              ,None),
                                            (OtherExpHits                ,None),
                                            (ReferencePeakPositions      ,None),
                                            (RelativeScore               ,None),
                                            (NormalisedScore             ,None),
                                            (MatchesScore                ,None),
                                            ))

# from ccpn.util.decorators import profile
# @profile
def hitsToDataFrame(project, spectrumHits, roiLeft=[6,10], roiRight=[0,5], roundPositionDecimals=3)-> pd.DataFrame:
    """
    Each column to be like Default_DataFrame. NB. One spectrum/Hit can have multiple references as could be a mixture of substances

    :param spectrumHits: list of Ccpn Obj spectrumHits
    :return: a data frame showing the details of the hits.
    """
    data = []
    for spectrumHit in spectrumHits:
        referenceSpectra = spectrumHit._getReferenceHitsSpectra()
        for referenceSpectrum in referenceSpectra:
            referenceSpectrum._referenceSpectrumHit = spectrumHit
            ## naming columns
            d = Default_DataFrame.copy()
            d[SpectrumHitPid] = str(spectrumHit.pid)
            d[ReferencePid] = str(referenceSpectrum.pid)
            d[ReferenceName] = str(referenceSpectrum.name)
            d[SpectrumHitName] = str(spectrumHit.spectrum.name)
            sample = spectrumHit._getSample()
            if sample:
                d[SampleName] = str(sample.name)
            d[ExperimentTypeName] = str(spectrumHit._getExperimentType())

            ##  Scoring columns
            referencePeakList = spectrumHit._getReferencePeakList(referenceSpectrum)
            if referencePeakList:
                peakHits = np.array(spectrumHit._getReferencePeakHits(referencePeakList))
                peakHitPos = np.array([round(p.position[0], 3) for p in peakHits])
                indPeakPos = np.where(np.logical_and(peakHitPos>=min(roiLeft), peakHitPos<=max(roiLeft)) |
                                     np.logical_and(peakHitPos >= min(roiRight), peakHitPos <= max(roiRight)))
                filteredPhits = list(peakHits[indPeakPos])
                if len(filteredPhits)>0:
                 ##  Positions columns
                    peakHitPos = [round(p.position[0],3) for p in filteredPhits]
                    snr = spectrumHit._getHitSNR(filteredPhits)
                    snrScore = np.mean(snr)
                    heights = [p.height for p in filteredPhits]
                    relScore = _scoreHits(heights)
                    deltas = spectrumHit._getDeltaPositionsFromPeaks(referencePeakList, filteredPhits)
                    matchScore = _scoreHits(deltas)

                    d[ReferenceTotalPeaksCount] = len(filteredPhits)
                    d[RelativeScore] = relScore
                    d[MatchesScore] = matchScore
                    d[SNR] = snrScore
                    d[ReferencePeakPositions] = peakHitPos
                    d[DeltaPositions] = deltas



            data.append(d)

    dataFrame = pd.DataFrame(data)
    levelsCount  = []
    levelsTypesL = []
    try:
        for ref, expType in zip(dataFrame[ReferencePid].values, dataFrame[ExperimentTypeName].values):
            spRef = project.getByPid(ref)
            levelCount, levelsTypes = _getReferenceLevel(spRef)
            levelsCount.append(int(levelCount))
            if expType in levelsTypes:
                levelsTypes.remove(expType)
                levelsTypesL.append(','.join(levelsTypes))


        dataFrame[ReferenceLevel] = levelsCount
        dataFrame[OtherExpHits] = levelsTypesL
        if RelativeScore in dataFrame:
            dataFrame[NormalisedScore] = _norm(dataFrame[RelativeScore])*100
    except: pass #for now as still testing

    return dataFrame