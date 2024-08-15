from libc.math cimport sqrt, sin, cos, M_PI

cdef class Vector:

    def __init__(self, double x, double y, double z):
        self.x = x
        self.y = y
        self.z = z


    def __mul__(self, Vector other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __pow__(self, double power):
        return Vector(self.x * power, self.y * power, self.z * power)

    def __sub__(self, Vector other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, Vector other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    cpdef double dot(self, Vector other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    cpdef Vector scale(self, double power):
        return Vector(self.x * power, self.y * power, self.z * power)

    cpdef double length(self):
        return sqrt(self.dot(self))

    cpdef Vector rotate_y(self, double angle):
        cdef double rad = angle * M_PI / 180.0
        cdef double cos_a = cos(rad)
        cdef double sin_a = sin(rad)
        return Vector(
            self.x * cos_a + self.z * sin_a,
            self.y,
            -self.x * sin_a + self.z * cos_a
        )
