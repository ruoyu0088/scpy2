import numpy as np
import cython

@cython.wraparound(False)
@cython.boundscheck(False)
def get_peaks(double[::1] x, double[::1] y, int n, x0=None, x1=None):
    cdef int i, j, index0, index1
    cdef double x_min, x_max, y_min, y_max, xc, yc, x_next, dx
    cdef double[::1] xr, yr

    if x0 is None:
        x0 = x[0]
    if x1 is None:
        x1 = x[len(x) - 1]

    index0, index1 = np.searchsorted(x, [x0, x1])
    index1 = min(index1, len(x) - 1)
    x0, x1 = x[index0], x[index1]
    dx = (x1 - x0) / n

    i = index0
    x_min = x_max = x[i]
    y_min = y_max = y[i]
    x_next = x0 + dx

    xr = np.empty(2 * n)
    yr = np.empty(2 * n)
    j = 0

    while True:
        xc, yc = x[i], y[i]
        if xc >= x_next or i == index1:
            if x_min > x_max:
                x_min, x_max = x_max, x_min
                y_min, y_max = y_max, y_min
            xr[j], xr[j + 1] = x_min, x_max
            yr[j], yr[j + 1] = y_min, y_max
            j += 2

            x_min = x_max = xc
            y_min = y_max = yc
            x_next += dx
            if i == index1:
                break
        else:
            if y_min > yc:
                x_min, y_min = xc, yc
            elif y_max < yc:
                x_max, y_max = xc, yc
        i += 1

    return xr.base[:j], yr.base[:j]