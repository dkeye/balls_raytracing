from .vector cimport Vector

cdef class Color(Vector):

    cdef int _in_range(self, double value)
