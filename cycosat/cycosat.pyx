from cpython cimport array
###1###
cdef extern from "picosat.h":
    ctypedef enum:
        PICOSAT_UNKNOWN
        PICOSAT_SATISFIABLE
        PICOSAT_UNSATISFIABLE        

    ctypedef struct PicoSAT:
        pass
    
    PicoSAT * picosat_init ()
    void picosat_reset (PicoSAT *)
    int picosat_add (PicoSAT *, int lit)
    int picosat_add_lits(PicoSAT *, int * lits)
    int picosat_sat (PicoSAT *, int decision_limit)
    int picosat_variables (PicoSAT *)
    int picosat_deref (PicoSAT *, int lit)
    void picosat_assume (PicoSAT *, int lit)
###1###
###2###
from cpython cimport array
    
cdef class CoSAT:
    
    cdef PicoSAT * sat
    cdef public array.array clauses #❶
    cdef int buf_pos   #❷

    def __cinit__(self):
        self.buf_pos = -1
        self.clauses = array.array("i", [0])  #❶
        
    def __dealloc__(self):
        self.close_sat()

    cdef close_sat(self):
        if self.sat is not NULL:
            picosat_reset(self.sat)
            self.sat = NULL
###2###
###3###
    cdef build_clauses(self):
        cdef int * p
        cdef int i
        cdef int count = len(self.clauses)
        if count - 1 == self.buf_pos:
            return
        p = self.clauses.data.as_ints #❶
        for i in range(self.buf_pos, count - 1):
            if p[i] == 0:
                picosat_add_lits(self.sat, p+i+1)
        self.buf_pos = count - 1
            
    cdef build_sat(self):  #❷
        if self.buf_pos == -1:
            self.close_sat()
            self.sat = picosat_init()
            if self.sat is NULL:
                raise MemoryError()
            self.buf_pos = 0
        self.build_clauses()
###3###
###4###
    cdef _add_clause(self, clause):
        self.clauses.extend(clause)
        self.clauses.append(0)
        
    def add_clause(self, clause):
        self._add_clause(clause)
        
    def add_clauses(self, clauses):
        for clause in clauses:
            self._add_clause(clause)
###4###
###5###
    def get_solution(self):
        cdef list solution = []
        cdef int i, v
        cdef int max_index
        
        max_index = picosat_variables(self.sat)  #❶
        for i in range(max_index):
            v = picosat_deref(self.sat, i+1)  #❷
            solution.append(v)
        return solution
               
    def solve(self, limit=-1):
        cdef int res
        self.build_sat()  #❸
        res = picosat_sat(self.sat, limit)  #❹
        if res == PICOSAT_SATISFIABLE:
            return self.get_solution()
        elif res == PICOSAT_UNSATISFIABLE:
            return "PICOSAT_UNSATISFIABLE"
        elif res == PICOSAT_UNKNOWN:
            return "PICOSAT_UNKNOWN"
###5###
###6###
    def iter_solve(self):
        cdef int res, i
        cdef list solution
        self.build_sat()
        while True:
            res = picosat_sat(self.sat, -1)
            if res == PICOSAT_SATISFIABLE:
                solution = self.get_solution()
                yield solution
                for i in range(len(solution)):
                    picosat_add(self.sat, -solution[i] * (i+1))   #❶
                picosat_add(self.sat, 0)
            else:
                break
        self.iter_reset()
        
    def iter_reset(self):  #❷
        self.buf_pos = -1
###6###
###7###
    def assume_solve(self, assumes):
        self.build_sat()
        for assume in assumes:
            picosat_assume(self.sat, assume)
        return self.solve()
###7###
###8###
    def get_failed_assumes(self):
        cdef int max_index
        cdef int ret1, ret0
        cdef list assumes = []
        self.build_sat()
        max_index = picosat_variables(self.sat)
        for i in range(1, max_index+1):
            picosat_assume(self.sat, i)
            ret1 = picosat_sat(self.sat, -1)
            picosat_assume(self.sat, -i)
            ret0 = picosat_sat(self.sat, -1)
            if ret0 == PICOSAT_UNSATISFIABLE:
                assumes.append(-i)
            if ret1 == PICOSAT_UNSATISFIABLE:
                assumes.append(i)
        return assumes
###8###
    