import numpy as np
from scipy import stats
import statsmodels.api as sm
import math
import time
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from scipy.stats import linregress
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from ccpn.util.Common import percentage
from scipy.interpolate import interp1d
import scipy.stats as ss

def exponential_func(x, a, b):
    """
    x array, a is the intercept, b is the slope
    """
    return a * np.exp(-b * x)

def exponenial_func2(t, A, T2, y0):
    return A*np.exp(-t/T2) + y0

def getXYtest1():

    x = np.random.rand(1000) * 10
    y = 10 * x + (5 + np.random.randn(1000) * 10 - 5)
    x.sort()
    return x,y

def getXYtest2():
    y = [16842176.0,  16713272.0, 13326191.0, 13532013.0,10659819.0, 8592719.0, 8503145.0]
    x = [0,45,50,100,300,500,800]
    return x,y

def getXYtest3():
    y = [25528778.0, 22926436.0, 23330148.0, 21522316.0, 11929308.0, 11482715.0, 9268095.0]
    x = [0, 45, 50, 100, 300, 500, 800]
    return x, y

def _getXY_SA1_SF_():
    """ project name SA1_ref.   spectra SP:SF_101-107 Peak at pos 7.006  assigned nmr atom 29 """
    y = [19767724.0, 18736124.0, 19697508.0, 19883436.0, 17006852.0, 18016828.0, 13259869.0]
    x = [0, 45, 50, 100, 300, 500, 800]
    return x, y

def _getXY_SA1_SP_():
    """ project name SA1_ref.  spectra SP:SP_101-107 Peak at pos 7.006  assigned nmr atom 29 """
    y = [15107357.0, 14314231.0, 14487850.0, 11855483.0, 8212651.0, 5989741.0, 5107460.0]
    x = [0, 45, 50, 100, 300, 500, 800]
    return x, y


def _getXY_Test4():
    y = [1.75, 0.90, 0.76, 0.50, 0.45, 0.30, 0.25, 0.20, 0.17, 0.15, 0.13, 0.12,0.11,0.115,0.114,0.113,0.1111]
    x = [0, 0.01, 0.03, 0.05, 0.07, 0.1, 0.11, 0.13,  0.15, 0.17, 0.2, 0.21, 0.23, 0.25, 0.27, 0.3,0.31]
    return x, y

def _getXY_Test4b():
    y = np.array([1.55, 1, 0.74, 0.60, 0.62, 0.27, 0.23, 0.20, 0.155, 0.133, 0.123, 0.112,0.101,0.1015,0.1,0.1,0.11])
    x = [0, 0.01, 0.03, 0.05, 0.07, 0.1, 0.11, 0.13,  0.15, 0.17, 0.2, 0.21, 0.23, 0.25, 0.27, 0.3,0.31]
    return x, y



# routines

def get_r2_numpy(x, y):
    slope, intercept = np.polyfit(x, y, 1)
    r_squared = 1 - (sum((y - (slope * x + intercept))**2) / ((len(y) - 1) * np.var(y, ddof=1)))
    return r_squared

def get_r2_scipy(x, y):
    _, _, r_value, _, _ = stats.linregress(x, y)
    return r_value**2

def get_r2_statsmodels(x, y):
    return sm.OLS(y, sm.add_constant(x)).fit().rsquared

def get_r2_python(x_list, y_list):
    n = len(x)
    x_bar = sum(x_list)/n
    y_bar = sum(y_list)/n
    x_std = math.sqrt(sum([(xi-x_bar)**2 for xi in x_list])/(n-1))
    y_std = math.sqrt(sum([(yi-y_bar)**2 for yi in y_list])/(n-1))
    zx = [(xi-x_bar)/x_std for xi in x_list]
    zy = [(yi-y_bar)/y_std for yi in y_list]
    r = sum(zxi*zyi for zxi, zyi in zip(zx, zy))/(n-1)
    return r**2

def get_r2_numpy_manual(x, y):
    zx = (x-np.mean(x))/np.std(x, ddof=1)
    zy = (y-np.mean(y))/np.std(y, ddof=1)
    r = np.sum(zx*zy)/(len(x)-1)
    return r**2

def get_r2_numpy_corrcoef(x, y):
    return np.corrcoef(x, y)[0, 1]**2

def correlateProfiles(array1, array2, engine='correlation'):
    """
    :param array1 and array2:  curves to compare. 1d or nd array
    :param engine: 'correlation' or 'spearmanr'.
    :return: correlation value (float 0 to 1)
    - if nd concatenate the single curves one after the other for array1 and 2 to create two single curves to be correlated.
    - If not of same lenght they'll be interpolated.
    - Apply np.corrcoef or spearmanr
    """

    corrcoef = None
    c1, c2 = array1, array2
    if array1.ndim >1 and array2.ndim >1:
        c1, c2 = np.concatenate(array1), np.concatenate(array2)
    if len(c1) != len(c2):  # we interpolate first to get same xs/ys length
        points = int(np.mean([len(c1),len(c2)]))
        x, x2 =  np.arange(len(c1)), np.arange(len(c2))
        xnew, xnew2 = np.linspace(min(x), max(x), num=points), np.linspace(min(x2), max(x2), num=points)
        f, f2 = interp1d(x, c1), interp1d(x2, c2)
        c1, c2 = f(xnew), f2(xnew2)
    if engine == 'correlation':
        corrcoef = np.corrcoef(c1, c2)[0][1]  # Gives back the correlation matrix for the two arrays
    if engine == 'spearmanr':
        spearmanr = ss.spearmanr(c1, c2)  # Gives the spearman correlation for the two arrays
        corrcoef = spearmanr.correlation
        pvalue = spearmanr.pvalue
    return corrcoef , c1, c2


if False:
    s = time.time()
    p_ = get_r2_python(x_list, y_list)
    f = time.time() -s
    print('Python %s. Time: %f' %(p_,f))

    s = time.time()
    # n_ = get_r2_numpy(x, y)
    f = time.time() -s
    print('Numpy polyfit %s. Time: %f' %(p_,f))

    s = time.time()
    nm_= get_r2_numpy_manual(x, y)
    f = time.time() -s
    print('Numpy Manual %s. Time: %f' %(p_,f))

    s = time.time()
    nc_ = get_r2_numpy_corrcoef(x, y)
    f = time.time() -s
    print('Numpy corrcoef %s. Time: %f' %(p_,f))

    s = time.time()
    sc_ = get_r2_scipy(x, y)
    f = time.time() -s
    print('Scipy %s. Time: %f' %(p_,f))

    s = time.time()
    st_ = get_r2_statsmodels(x, y)
    f = time.time() -s
    print('Statsmodels %s. Time: %f' %(p_,f))

    s = time.time()
    sk_ = r2_score(y,x)
    f = time.time() -s
    print('SK %s. Time: %f' %(sk_,f))

    s = time.time()
    slope_f, intercept_f, r_value_f, p_value_f, std_err_f = linregress(x, y)
    f = time.time() -s
    print('SLOPE',slope_f, 'intercept_f', intercept_f)
    print('Lin %s. Time: %f' %(r_value_f**2,f))

def percentageChange(v1, v2):
    """
    |𝑉1−𝑉2|[(𝑉1+𝑉2)2
    """
    n = abs(v1-v2)
    d = (v1+v2)/2
    return (n/d)*100

def calculateFit(x,y, label = ''):
    xs, ys = x,y
    p0=(1,0)
    z = (ys-np.min(ys))/(np.max(ys)-np.min(ys))
    popt, pcov = curve_fit(exponential_func, xs, z, p0=p0)
    interc, slope = popt
    # xfMax = np.max(xs)
    # xf = np.arange(0, xfMax)

    xfRange = np.max(xs) - np.min(xs)
    xfPerc = percentage(60, xfRange)
    xfMax = np.max(xs) + xfPerc
    print(xfMax, 'eee')
    xf = np.arange(0, xfMax, step=0.01)
    popt, pcov = curve_fit(exponential_func, xs, z, p0=[interc, slope])
    interc, slope = popt
    yf = exponential_func(xf, *popt)
    R2_rf = get_r2_statsmodels(xf, yf)
    print('slope fit ' + label, slope, )
    print('interc fit' + label, interc, )
    print('R2 fit' + label, R2_rf, )
    print('Uncertainty on constant =' + label, np.sqrt(pcov[0, 0]))
    std_err = np.sqrt(np.diag(pcov))
    print('std_err' + label,std_err)
    return xf,yf, xs, z, slope, interc, R2_rf, std_err

# print(r2_score(y, yf))
# plt.plot(yintercept_ff)

x,y = _getXY_Test4()
xSP,ySP = _getXY_Test4b()


plotItCurve = False
if plotItCurve:
    plt.plot(x,y, '--b', label='Test')
    plt.legend()
    plt.plot(x, y)
    plt.show()

xf,yf, xs, z, slope, interc, R2_rf, std_err = calculateFit(x,y, 'SF')
xf_SP,yf_SP, xs_SP, z_SP, slope_SP, interc_SP, R2_rf_SP, std_err_SP = calculateFit(xSP,ySP, 'SP')

fLine = 1/slope
pLine = 1/slope_SP

changeSlope =  percentageChange(slope,slope_SP)
cor = correlateProfiles(z, z_SP)
# print('correlateProfiles: %f. changeSlope:%f'% (cor,changeSlope))


import pandas as pd
# print('changeSlope',changeSlope)
SavePath = '/Users/luca/Desktop/DFCI/cpmg_development/bindingCurves/'

# page3
from tqdm import tqdm
from collections import OrderedDict as od
t = time.time()
# with pd.ExcelWriter(SavePath+'test.xlsx') as writer:
#     dfs = od([('scaled',(xs_SP, z_SP)),
#               ('fitted',(xf_SP,yf_SP))])
#     for name in tqdm(dfs):
#         xx,yy = dfs.get(name)
#         df = pd.DataFrame(yy)
#         df = df.transpose() # faster the creating the columns from a list (for large dataset huge diff)
#         # df.columns = xx
#         df.to_excel(writer, sheet_name=name)
#     writer.save()
# print(time.time()-t,)

ffLine = yf[xf<=fLine]

plotFit = True
if plotFit:
    fig = plt.figure(dpi=100)
    plt.plot(xf,yf, 'r', label='fitted f')
    plt.plot(xf_SP, yf_SP, 'b', label='fitted p')

    plt.plot(xs, z, 'or',)
    plt.plot(xs_SP, z_SP, '*b')

    # plt.plot([fLine]*100,np.arange(0,1,0.01), '--r')
    # plt.plot([pLine] * 100, np.arange(0, 1, 0.01), '--b')
    plt.plot(np.arange(0, 1, 0.01),[0.367] * 100, '--')
    plt.legend()
    text1 = ' SF Slope: %0.4f Intercept: %0.4f R2: %0.4f std_err Slope: %0.4f ' % (slope, interc, R2_rf, std_err[0])
    text2 = ' SP Slope: %0.4f Intercept: %0.4f R2: %0.4f std_err Slope: %0.4f ' % (slope_SP, interc_SP, R2_rf_SP, std_err_SP[0])
    fig.text(0.5, 0.03, text1, ha='center')
    fig.text(0.5, 0.01, text2, ha='center')
    plt.show()

