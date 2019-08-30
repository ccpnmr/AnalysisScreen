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
__dateModified__ = "$dateModified: 2017-07-07 16:32:26 +0100 (Fri, July 07, 2017) $"
__version__ = "$Revision: 3.0.0 $"
#=========================================================================================
# Created
#=========================================================================================
__author__ = "$Author: Luca Mureddu $"
__date__ = "$Date: 2017-04-07 10:28:42 +0000 (Fri, April 07, 2017) $"
#=========================================================================================
# Start of code
#=========================================================================================


import numpy as np
# import pandas as pd

from collections import namedtuple
# from math import sin, cos, pi, log
import os
import decimal


FIELD = 400
SW_PPM = 14
CENTER = 4.7
POINTS = 2 ** 14

spectrum_x_ppm = np.linspace(CENTER + SW_PPM / 2, CENTER - SW_PPM / 2, POINTS)
spectrum_x_hz = spectrum_x_ppm * FIELD


def _lorentzian(points, center, linewidth, intensity=1, phase=0):
    points = np.asarray(points)
    tau = 2 / linewidth
    delta = center - points
    x = delta * tau

    absorptive = (1 / (1 + x ** 2)) / linewidth
    normCoeff = absorptive.max()

    return intensity * absorptive / normCoeff


def _spectrumFromPeaks(x, peaks):
    spectrum = np.zeros(len(x))
    for peak in peaks:
        subspec = _lorentzian(x, peak.frequency, peak.linewidth, intensity=peak.intensity, phase=peak.phase)
        spectrum += subspec
    return spectrum


def _writeBruker(directory, data):
    dic = {'BYTORDP': 0,  # Byte order, little (0) or big (1) endian
           'NC_proc': 0,  # Data scaling factor, -3 means data were multiplied by 2**3, 4 means divided by 2**4
           'SI'     : POINTS,  # Size of processed data
           'XDIM'   : 0,  # Block size for 2D & 3D data
           'FTSIZE' : POINTS,  # Size of FT output.  Same as SI except for strip plotting.
           'SW_p'   : SW_PPM * FIELD,  # Spectral width of processed data in Hz
           'SF'     : FIELD,  # Spectral reference frequency (center of spectrum)
           'OFFSET' : SW_PPM / 2 + CENTER,  # ppm value of left-most point in spectrum
           'AXNUC'  : '<1H>',
           'LB'     : 5.0,  # Lorentzian broadening size (Hz)
           'GB'     : 0,  # Gaussian broadening factor
           'SSB'    : 0,  # Sine bell shift pi/ssb.  =1 for sine and =2 for cosine.  values <2 default to sine
           'WDW'    : 1,  # Window multiplication mode
           'TM1'    : 0,  # End of the rising edge of trapezoidal, takes a value from 0-1, must be less than TM2
           'TM2'    : 1,  # Beginings of the falling edge of trapezoidal, takes a value from 0-1, must be greater than TM1
           'BC_mod' : 0  # Baseline correction mode (em, gm, sine, qsine, trap, user(?), sinc, qsinc, traf, trafs(JMR 71 1987, 237))
           }

    procDir = 'pdata/1'
    realFileName = '1r'
    try:
        os.makedirs(os.path.join(directory, procDir))
    except FileExistsError:
        pass

    specMax2 = np.log2(data.max())
    factor = int(29 - specMax2)
    data = data * 2 ** factor
    dic['NC_proc'] = -factor

    with open(os.path.join(directory, procDir, 'procs'), 'w') as f:
        for k in sorted(dic.keys()):
            f.write('##${}= {}\n'.format(k, dic[k]))

    with open(os.path.join(directory, procDir, realFileName), 'wb') as f:
        f.write(data.astype('<i4').tobytes())
