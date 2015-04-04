# -*- coding: utf-8 -*-
#cython: boundscheck=False, wraparound=False
###1###
from libc.math cimport log2
import numpy as np
import cython

cdef double iter_point(complex c, int n, double R):
    cdef complex z = c
    cdef int i
    cdef double r2, mu
    cdef double R2 = R*R
    for i in range(1, n):
        r2 = z.real*z.real + z.imag*z.imag
        if r2 > R2: break 
        z = z * z + c
    if r2 > 4.0:
        mu = i - log2(0.5 * log2(r2))
    else:
        mu = i
    return mu

def mandelbrot(double cx, double cy, double d, int h=0, int w=0, 
               double[:, ::1] out=None, int n=20, double R=10.0):
    cdef double x0, x1, y0, y1, dx, dy
    cdef double[:, ::1] r 
    cdef int i, j
    cdef complex z
    x0, x1, y0, y1 = cx - d, cx + d, cy - d, cy + d
    if out is not None:
        r = out
    else:
        r = np.zeros((h, w))
    h, w = r.shape[0], r.shape[1]
    dx = (x1 - x0) / (w - 1)
    dy = (y1 - y0) / (h - 1)
    for i in range(h):
        for j in range(w):
            z.imag = y0 + i * dy
            z.real = x0 + j * dx
            r[i, j] = iter_point(z, n, R)
    return r.base 
###1###
    
cdef class IFS:
    cdef double[::1] rx, ry
    cdef object count
    cdef int n, size
    cdef double x0, x1, y0, y1, inv_delta, dx, dy
    cdef double x, y
    cdef int[::1] select
    cdef double[:, ::1] eq
    
    def __cinit__(self, p, eq, int n, int size=100):
        self.n = n
        self.size = size
        self.rx = np.zeros(n)
        self.ry = np.zeros(n)
        self.x = self.y = 0.0
        self.select = np.searchsorted(np.cumsum(p), np.random.rand(n))
        self.eq = eq
        
    def shuffle(self):
        idx1 = np.random.randint(0, self.n, self.n//2)
        idx2 = np.random.randint(0, self.n, self.n//2)
        arr = self.select.base
        tmp = arr[idx1]
        arr[idx1] = arr[idx2]
        arr[idx2] = tmp
                
    def iterate(self, int n):
        cdef int[::1] select
        cdef double a, b, c, d, e, f, x, y
        cdef double[::1] rx, ry
        cdef double[:, ::1] eq
        cdef int i, j
        
        x = self.x
        y = self.y
        select = self.select
        eq = self.eq
        rx = self.rx
        ry = self.ry        
        self.shuffle()

        for i in range(n):
            j = select[i] * 2
            a, b, c = eq[j,   0], eq[j,   1], eq[j,   2]
            d, e, f = eq[j+1, 0], eq[j+1, 1], eq[j+1, 2]
            x, y = a*x + b*y + c, d*x + e*y + f            
            rx[i] = x
            ry[i] = y
        self.x = x
        self.y = y
        
    def update(self):
        cdef double[::1] rx, ry
        cdef int[:, ::1] count
        cdef double a, b, c, d, e, f, inv_delta, x0, y0
        cdef int i, j, w, h, col, row
        
        if self.count is None:
            self.iterate(1000)
        
        self.iterate(self.n)
            
        if self.count is None:
            self.x0 = np.min(self.rx)
            self.x1 = np.max(self.rx)
            self.y0 = np.min(self.ry)
            self.y1 = np.max(self.ry)
            dx = (self.x1 - self.x0) * 0.05
            dy = (self.y1 - self.y0) * 0.05
            self.x0 -= dx
            self.x1 += dx
            self.y0 -= dy
            self.y1 += dy
            self.inv_delta = self.size / max(self.x1-self.x0, self.y1-self.y0)
            h = int((self.y1 - self.y0) * self.inv_delta)
            w = int((self.x1 - self.x0) * self.inv_delta)
            if h > 0 and w > 0:
                self.count = np.ones((h, w), np.int)
                
        if self.count is None:
            return None

        x0 = self.x0
        y0 = self.y0
        inv_delta = self.inv_delta
        count = self.count
        rx = self.rx
        ry = self.ry
        h, w = count.shape[0], count.shape[1]
        
        for i in range(self.n):
            row = int((ry[i]-y0)*inv_delta)
            col = int((rx[i]-x0)*inv_delta)
            row = min(max(row, 0), h-1)
            col = min(max(col, 0), w-1)
            count[row, col] += 1        

        return self.count
