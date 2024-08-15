from .vector cimport Vector
from .color cimport Color

cdef class Sphere:
    cdef public Vector center
    cdef public int radius
    cdef public tuple color
    cdef public int specular
    cdef public double reflective

cdef class Light:
    cdef public str type
    cdef public double intensity
    cdef public Vector position
    cdef public Vector direction

cpdef Color trace_ray(Vector origin, Vector direction_ray, double t_min, double t_max, int depth, list spheres, list lights, Color background_color)
