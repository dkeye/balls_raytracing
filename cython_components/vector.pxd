cdef class Vector:
    cdef public double x, y, z

    cpdef double dot(self, Vector other)
    cpdef Vector scale(self, double power)
    cpdef double length(self)
    cpdef Vector rotate_y(self, double angle)


