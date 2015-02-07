#cython: boundscheck=False
#cython: wraparound=False

cimport cython
from cpython cimport mem
###8###
cdef add_array(double *op1, double *op2, double *res, int count):
    cdef int i
    for i in range(count):
        res[i] = op1[i] + op2[i]

cdef add_number(double *op1, double op2, double *res, int count):
    cdef int i
    for i in range(count):
        res[i] = op1[i] + op2
###8###
###1###
cdef class Vector:
    cdef int count
    cdef double * data
###1###
###2###    
    def __cinit__(self, data):
        cdef int i
        if isinstance(data, int):
            self.count = data
        else:
            self.count = len(data)
        self.data = <double *>mem.PyMem_Malloc(sizeof(double)*self.count)
        if self.data is NULL:
            raise MemoryError
        
        if not isinstance(data, int):
            for i in range(self.count):
                self.data[i] = data[i]
###2###
###3###                
    def __dealloc__(self):
        if self.data is not NULL:
            mem.PyMem_Free(self.data)
###3###
###4###            
    def __len__(self):
        return self.count
    
    cdef _check_index(self, int *index):
        if index[0] < 0:
            index[0] = self.count + index[0]
        if index[0] < 0  or index[0] > self.count - 1:
            raise IndexError("Vector index out of range")
    
    def __getitem__(self, int index):
        self._check_index(&index)
        return self.data[index]
    
    def __setitem__(self, int index, double value):
        self._check_index(&index)
        self.data[index] = value
###4###
###5###        
    def __add__(self, other):
        cdef Vector new, _self, _other

        if not isinstance(self, Vector): #❶
            self, other = other, self
        _self = <Vector>self #❸

        if isinstance(other, Vector): #❷       
            _other = <Vector>other #❸
            if _self.count != _other.count:
                raise ValueError("Vector size not equal")
            new = Vector(_self.count) #❹
            add_array(_self.data, _other.data, new.data, _self.count)
            return new 
        new = Vector(_self.count) #❹
        add_number(_self.data, <double>other, new.data, _self.count)
        return new
###5###
###6###        
    def __iadd__(self, other):
        cdef Vector _other
        if isinstance(other, Vector):
            _other = <Vector>other
            if self.count != _other.count:
                raise ValueError("Vector size not equal")
            add_array(self.data, _other.data, self.data, self.count)
        else:
            add_number(self.data, <double>other, self.data, self.count)
        return self
###6###
###7###        
    def __str__(self):
        values = ", ".join(str(self.data[i]) for i in range(self.count))
        norm = self.norm()
        return "Vector[{}]({})".format(norm, values)
    
    cpdef norm(self):
        cdef double *p
        cdef double s
        cdef int i
        s = 0
        p = self.data
        for i in range(self.count):
            s += p[i] * p[i]
        return s**0.5
###7###