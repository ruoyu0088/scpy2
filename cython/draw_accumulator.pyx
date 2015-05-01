#cython: cdivision=True
#cython: boundscheck=False
#cython: wraparound=False

import numpy as np
cimport numpy as np
from libc.math cimport ceil

cdef unsigned char point_in_polygon(double[::1] xp, double[::1] yp,
                                           double x, double y):
    cdef Py_ssize_t i
    cdef unsigned char c = 0
    cdef Py_ssize_t j = xp.shape[0] - 1
    for i in range(xp.shape[0]):
        if (
            (((yp[i] <= y) and (y < yp[j])) or
            ((yp[j] <= y) and (y < yp[i])))
            and (x < (xp[j] - xp[i]) * (y - yp[i]) / (yp[j] - yp[i]) + xp[i])
        ):
            c = not c
        j = i
    return c


cdef class DrawAccumulator:
    
    cdef int width, height
    cdef int[:, ::1] count_buf
    cdef double[:, ::1] sum_buf
    
    def __cinit__(self, width, height):
        self.width = width
        self.height = height
        shape = (height, width)
        self.count_buf = np.zeros(shape, dtype=int)
        self.sum_buf = np.zeros(shape, dtype=float)
        
    def reset(self):
        self.count_buf[:, :] = 0
        self.sum_buf[:, :] = 0
        
    def add_polygon(self, xa, ya, double value):
        cdef Py_ssize_t minr = int(max(0, np.min(ya)))
        cdef Py_ssize_t maxr = int(ceil(np.max(ya)))
        cdef Py_ssize_t minc = int(max(0, np.min(xa)))
        cdef Py_ssize_t maxc = int(ceil(np.max(xa)))

        cdef double[::1] x = xa
        cdef double[::1] y = ya

        cdef Py_ssize_t r, c
        
        maxr = min(self.height - 1, maxr)
        maxc = min(self.width  - 1, maxc)

        for r in range(minr, maxr+1):
            for c in range(minc, maxc+1):
                if point_in_polygon(x, y, c, r):
                    self.count_buf[r, c] += 1
                    self.sum_buf[r, c] += value
                    
    def add_lines(self, Py_ssize_t[:, ::1] lines, double[::1] values):
        cdef char steep = 0
        cdef Py_ssize_t sx, sy, d, i, idx, r, c, dx, dy, x, y, x2, y2
        cdef int w = self.width
        cdef int h = self.height

        for idx in range(lines.shape[0]):
            steep = 0
            x = lines[idx, 0]
            y = lines[idx, 1]
            x2 = lines[idx, 2]
            y2 = lines[idx, 3]

            dx = x2 - x
            dy = y2 - y
            if dx < 0:
                dx = -dx
            if dy < 0:
                dy = -dy

            sx = 1 if (x2 - x) > 0 else -1
            sy = 1 if (y2 - y) > 0 else -1

            if dy > dx:
                steep = 1
                x, y = y, x
                dx, dy = dy, dx
                sx, sy = sy, sx

            d = (2 * dy) - dx

            for i in range(dx):
                if steep:
                    r = x
                    c = y
                else:
                    r = y
                    c = x
                if 0 <= r < h and 0 <= c < w:
                    self.count_buf[r, c] += 1
                    self.sum_buf[r, c] += values[idx]

                while d >= 0:
                    y = y + sy
                    d = d - (2 * dx)
                x = x + sx
                d = d + (2 * dy)

            r = y2
            c = x2
            if 0 <= r < h and 0 <= c < w:
                self.count_buf[r, c] += 1
                self.sum_buf[r, c] += values[idx]
                
    def mean(self):
        count_buf = self.count_buf.base
        sum_buf = self.sum_buf.base
        mean_buf = np.zeros_like(sum_buf)
        mask = count_buf > 0
        mean_buf[mask] = sum_buf[mask] / count_buf[mask]
        return mean_buf
    
    def count(self):
        return self.count_buf.base
    
    def sum(self):
        return self.sum_buf.base