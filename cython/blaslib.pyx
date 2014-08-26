import cython
import numpy as np
from cython.parallel import prange
from cpython cimport PyCObject_AsVoidPtr
from scipy.linalg import blas

ctypedef void (*saxpy_ptr) (const int *N, const float *alpha, 
                            const float *X, const int *incX, float *Y, const int *incY) nogil
cdef saxpy_ptr _saxpy=<saxpy_ptr>PyCObject_AsVoidPtr(blas.saxpy._cpointer)

ctypedef void (*daxpy_ptr) (const int *N, const double *alpha, 
                            const double *X, const int *incX, double *Y, const int *incY) nogil
cdef daxpy_ptr _daxpy=<daxpy_ptr>PyCObject_AsVoidPtr(blas.daxpy._cpointer)


def saxpy(float[:] y, float a, float[:] x):
    cdef int n = y.shape[0]
    cdef int inc_x = x.strides[0] / sizeof(float)
    cdef int inc_y = y.strides[0] / sizeof(float)
    _saxpy(&n, &a, &x[0], &inc_x, &y[0], &inc_y)
    
def daxpy(double[:] y, double a, double[:] x):
    cdef int n = y.shape[0]
    cdef int inc_x = x.strides[0] / sizeof(double)
    cdef int inc_y = y.strides[0] / sizeof(double)
    _daxpy(&n, &a, &x[0], &inc_x, &y[0], &inc_y)
    
ctypedef void (*dgemm_ptr) (char *ta, char *tb, 
                            int *m, int *n, int *k,
                            double *alpha,
                            double *a, int *lda,
                            double *b, int *ldb,
                            double *beta,
                            double *c, int *ldc) nogil

cdef dgemm_ptr _dgemm=<dgemm_ptr>PyCObject_AsVoidPtr(blas.dgemm._cpointer)


@cython.wraparound(False)
@cython.boundscheck(False)
def dgemm(double[:, :, :] A, double[:, :, :] B, int[:, ::1] index):
    cdef int m, n, k, i, length, idx_a, idx_b
    cdef double[:, :, :] C
    cdef char ta, tb
    cdef double alpha = 1.0
    cdef double beta = 0.0
        
    length = index.shape[0]
    m, k, n  = A.shape[1], A.shape[2], B.shape[2]        
    
    C = np.zeros((length, n, m))
    
    ta = "T"
    tb = ta
    
    for i in prange(length, nogil=True):
        idx_a = index[i, 0]
        idx_b = index[i, 1]
        _dgemm(&ta, &tb, &m, &n, &k, &alpha, 
               &A[idx_a, 0, 0], &k, 
               &B[idx_b, 0, 0], &n, 
               &beta,
               &C[i, 0, 0], &m)
    
    return C.base

    
def matrix_multiply(a, b):
    if a.ndim <= 2 and b.ndim <= 2:
        return np.dot(a, b)
    
    a = np.ascontiguousarray(a).astype(np.float, copy=False)
    b = np.ascontiguousarray(b).astype(np.float, copy=False)
    if a.ndim == 2:
        a = a[None, :, :]
    if b.ndim == 2:
        b = b[None, :, :]
        
    shape_a = a.shape[:-2]
    shape_b = b.shape[:-2]
    len_a = np.prod(shape_a)
    len_b = np.prod(shape_b)
    
    idx_a = np.arange(len_a, dtype=np.int32).reshape(shape_a)
    idx_b = np.arange(len_b, dtype=np.int32).reshape(shape_b)
    idx_a, idx_b = np.broadcast_arrays(idx_a, idx_b)
    
    index = np.column_stack((idx_a.ravel(), idx_b.ravel()))
    bshape = idx_a.shape
    
    if a.ndim > 3:
        a = a.reshape(-1, a.shape[-2], a.shape[-1])
    if b.ndim > 3:
        b = b.reshape(-1, b.shape[-2], b.shape[-1])
    
    if a.shape[-1] != b.shape[-2]:
        raise ValueError("can't do matrix multiply because k isn't the same")

    c = dgemm(a, b, index)
    c = np.swapaxes(c, -2, -1)
    c.shape = bshape + c.shape[-2:]
    return c