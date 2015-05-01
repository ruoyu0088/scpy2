# -*- coding: utf-8 -*-
###1###
cdef extern from "ahocorasick.h": #❶
    ctypedef int (*AC_MATCH_CALBACK_f)(AC_MATCH_t *, void *) #❷
    ctypedef enum AC_STATUS_t: #❸
        ACERR_SUCCESS = 0
        ACERR_DUPLICATE_PATTERN
        ACERR_LONG_PATTERN
        ACERR_ZERO_PATTERN
        ACERR_AUTOMATA_CLOSED

    ctypedef struct AC_MATCH_t: #❹
        AC_PATTERN_t * patterns
        long position
        unsigned int match_num

    ctypedef struct AC_AUTOMATA_t:
        AC_MATCH_t match

    ctypedef struct AC_PATTERN_t:
        char * astring
        unsigned int length

    ctypedef struct AC_TEXT_t:
        char * astring
        unsigned int length

    #❺
    AC_AUTOMATA_t * ac_automata_init() 
    AC_STATUS_t ac_automata_add(AC_AUTOMATA_t * thiz, AC_PATTERN_t * pattern)
    void ac_automata_finalize(AC_AUTOMATA_t * thiz)
    int ac_automata_search(AC_AUTOMATA_t * thiz, AC_TEXT_t * text, int keep, 
        AC_MATCH_CALBACK_f callback, void * param)
    void ac_automata_settext (AC_AUTOMATA_t * thiz, AC_TEXT_t * text, int keep)
    AC_MATCH_t * ac_automata_findnext (AC_AUTOMATA_t * thiz)        
    void ac_automata_release(AC_AUTOMATA_t * thiz)
###1###

###4###
cdef int isin_callback(AC_MATCH_t * match, void * param):
    cdef MultiSearch ms = <MultiSearch> param #❶
    ms.found = True  #❷
    return 1  #❸
###4###
###6###
cdef int search_callback(AC_MATCH_t * match, void * param):
    cdef MultiSearch ms = <MultiSearch> param
    cdef bytes pattern = match.patterns.astring
    cdef int res = 1
    try:
        res = ms.callback(match.position - len(pattern), pattern)  #❶
    except Exception as ex:
        import sys
        ms.exc_info = sys.exc_info()  #❷
    return res
###6###   

###2###
cdef class MultiSearch:
    
    cdef AC_AUTOMATA_t * _auto #❶
    cdef bint found
    cdef object callback
    cdef object exc_info

    def __cinit__(self, keywords):
        self._auto = ac_automata_init()
        if self._auto is NULL:
            raise MemoryError
        self.add(keywords) #❷

    def __dealloc__(self):
        if self._auto is not NULL:
            ac_automata_release(self._auto)
            
    cdef add(self, keywords):
        cdef AC_PATTERN_t pattern
        cdef bytes keyword
        cdef AC_STATUS_t err
        
        for keyword in keywords: #❸
            pattern.astring = <char *>keyword
            pattern.length = len(keyword)
            err = ac_automata_add(self._auto, &pattern)
            if err != ACERR_SUCCESS:
                raise ValueError("Error Code:%d" % err)

        ac_automata_finalize(self._auto)
###2###

###3###
    def isin(self, bytes text, bint keep=False):
        cdef AC_TEXT_t temp_text   #❶
        temp_text.astring = <char *>text
        temp_text.length = len(text)
        self.found = False         #❷
        ac_automata_search(self._auto, &temp_text, keep, isin_callback, <void *>self) #❸
        return self.found
###3###

###5###
    def search(self, bytes text, callback, bint keep=False):
        cdef AC_TEXT_t temp_text
        temp_text.astring = <char *>text
        temp_text.length = len(text)
        self.found = False
        self.callback = callback  #❶
        self.exc_info = None
        ac_automata_search(self._auto, &temp_text, keep, search_callback, <void *>self) #❷
        if self.exc_info is not None:
            raise self.exc_info[1], None, self.exc_info[2]  #❸
###5###
###7###
    def iter_search(self, bytes text, bint keep=False):
        cdef AC_TEXT_t temp_text
        cdef AC_MATCH_t * match
        cdef bytes matched_pattern
        temp_text.astring = <char *>text
        temp_text.length = len(text)
        ac_automata_settext(self._auto, &temp_text, keep)
        while True:
            match = ac_automata_findnext(self._auto)
            if match == NULL:
                break
            matched_pattern = <bytes>match.patterns.astring
            yield match.position - len(matched_pattern), matched_pattern
###7###