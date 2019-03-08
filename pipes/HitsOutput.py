

'''
Create a new Pandas dataFrame from SpectrumHits obtained from a pipeline
'''

import pandas as pd
from ccpn.core.SpectrumHit import _getReferenceLevel, scoreHit, _norm, _grade, _scoreMatches

import collections
from ccpn.core.PeakList import _estimateNoiseLevel1D, _estimateSNR1D
from sklearn.preprocessing import minmax_scale
import numpy as np
# Naming
RefPid = 'Pid'
ReferenceName = 'Reference'                      # -> Str | name of the spectrum used as reference
SpectrumHitName = 'SpectrumHit'                  # -> Str | name of the spectrum used to identified the hits. Like STDs of sample with target
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
                                            (ReferenceTotalScore         ,None),
                                            (ReferenceFigureOfMerit      ,None),
                                            (ReferenceTotalPeaksCount    ,None),
                                            (ReferenceLevel              ,None),
                                            (ReferencePeakPositions      ,None),
                                            (RelativeScore               ,None),
                                            (NormalisedScore             ,None),
                                            (MatchesScore                ,None),
                                            ))


def hitsToDataFrame(spectrumHits)-> pd.DataFrame:
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
            d[RefPid] = str(referenceSpectrum.pid)
            d[ReferenceName] = str(referenceSpectrum.name)
            d[SpectrumHitName] = str(spectrumHit.spectrum.name)
            sample = spectrumHit._getSample()
            if sample:
                d[SampleName] = str(sample.name)
            d[ExperimentTypeName] = str(spectrumHit._getExperimentType())

            ##  Scoring columns
            referencePeakList = spectrumHit._getReferencePeakList(referenceSpectrum)
            if referencePeakList:
                referenceTotalScore = spectrumHit._getSingleScore(referencePeakList)
                if referenceTotalScore:
                    d[ReferenceTotalScore] = float(referenceTotalScore)
                referenceTotalPeaksCount = spectrumHit._getSinglePeakCount(referencePeakList)
                if referenceTotalPeaksCount:
                    d[ReferenceTotalPeaksCount] = int(referenceTotalPeaksCount)
                 ##  Positions columns
                refpeakHits = spectrumHit._getReferencePeakHits(referencePeakList)
                refpeakHitPos = [p.position for p in refpeakHits]
                d[ReferencePeakPositions] = refpeakHitPos
                # deltas = [round(lp.position[0] - p.position[0], 4)
                #      for p in spectrumHit._getPeakHits() for lp in p._linkedPeaks if lp in referencePeakList.peaks]
                deltas= spectrumHit._getDeltaPositions(referencePeakList)
                d[DeltaPositions] = deltas
                heights = spectrumHit._getHitHeights(spectrumHit._getPeakHits())
                snr = spectrumHit.spectrum._snr
                nl = spectrumHit.spectrum.noiseLevel
                # if snr is None:
                #     snr = _estimateSNR1D(spectrumHit.spectrum.intensities)
                #     spectrumHit.spectrum._snr = snr
                # relScore = scoreHit(heights,snr)
                matchScore = _scoreMatches(deltas)
                d[MatchesScore] = matchScore
                # relScore = np.sum(np.array(heights)-nl)
                relScore = _scoreMatches(heights)
                d[RelativeScore] = relScore
                d[SNR] = snr
            ##  level column
            level = _getReferenceLevel(spectrumHit.project, referenceSpectrum)
            d[ReferenceLevel] = int(level)
            data.append(d)

    dataFrame = pd.DataFrame(data)
    if RelativeScore in dataFrame:
        dataFrame[NormalisedScore] = _norm(dataFrame[ReferenceTotalScore])*100

    return dataFrame