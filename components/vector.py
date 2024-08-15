from math import sqrt, cos, sin, radians
from typing import Union


class Vector:
    def __init__(self, x: Union[int, float], y: Union[int, float], z: Union[int, float]):
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other: 'Vector') -> int:
        """Dot product of two 3D vectors."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __pow__(self, power: Union[float, int]) -> 'Vector':
        """Computes k * vec"""
        return Vector(self.x * power, self.y * power, self.z * power)

    def __rpow__(self, power):
        """Computes k * vec"""
        return self.__pow__(power)

    def __sub__(self, other: 'Vector') -> 'Vector':
        """Computes v1 - v2"""
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other: 'Vector') -> 'Vector':
        """Computes v1 + v2"""
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    @property
    def length(self):
        """Length of a 3D vector."""
        return sqrt(self.__mul__(self))

    def rotate_y(self, angle: float) -> 'Vector':
        """Вращает вектор вокруг оси Y на заданный угол."""
        rad = radians(angle)
        cos_a = cos(rad)
        sin_a = sin(rad)
        return Vector(
            self.x * cos_a + self.z * sin_a,
            self.y,
            -self.x * sin_a + self.z * cos_a
        )
