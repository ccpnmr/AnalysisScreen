import numpy as np
from scipy.signal import correlate
import matplotlib.pyplot as plt
from scipy.optimize import fmin
from scipy import signal
def yvals1(x):
    return np.sin(x)+np.sin(2*x)+np.sin(3*x)


def yvals2(x):
  return np.sin(x) + np.sin(3 * x) + np.sin(3 * x)

def err_func(p, x1,x2, y1,y2):
    return np.sqrt((x1-x2+p[0])**2+(y1-y2)**2).sum()

def _getShift(ref_x, ref_y, target_y):
  '''
  :param ref_x: X array of the reference spectra (positions)
  :param ref_y: Y array of the reference spectra (intensities)
  :param target_y: Y array of the target spectra (intensities)
  :return: the shift needed to align the two spectra.
  To align the target spectrum to its reference: add the shift to the x array.
  E.g. target_y += shift
  '''
  return (np.argmax(signal.correlate(ref_y, target_y)) - len(target_y)) * np.mean(np.diff(ref_x))




#
#
# dx = .1
# unknown_shift = .03 * np.random.random() * dx
#
# X1  = np.arange(0,2*np.pi,dx)  #some X values
# X2  = X1 + unknown_shift
#
# Y1 = yvals1(X1)
# Y2 = yvals2(X2) # shifted Y
#
# print("Unknown shift: ", unknown_shift)
# print("Found   shift: ", found_shift)
# print ("Percent error: ", abs((unknown_shift-found_shift)/unknown_shift))

target =   [0, 0, 0, 1, 2, 3, 2, 1, 0, 0]
compound = [0, 0,  1, 2, 3, 2, 1, 0, 0, 0]

# Y2 += .1*np.random.normal(size=X1.shape)  # now with noise

x_target = np.arange(len(target))
y_target = np.array(target)

x_compound = np.arange(len(compound))
y_compound = np.array(compound)



s = _getShift(x_target, y_target, y_compound)


print(s)
plt.plot(y_target)
plt.plot(y_compound)




plt.legend(("target", "compound",))

plt.show()