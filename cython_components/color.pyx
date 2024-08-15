from .vector cimport Vector

cdef class Color(Vector):
    def __init__(self, double r, double g, double b):
        super().__init__(self._in_range(r), self._in_range(g), self._in_range(b))

    cdef int _in_range(self, double value):
        return min(255, max(0, <int>value))

    def as_tuple(self) -> tuple[int, int, int]:
        return self.x, self.y, self.z
