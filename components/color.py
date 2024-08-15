from components.vector import Vector


class Color(Vector):
    def __init__(self, r: int, g: int, b: int):
        super().__init__(r, g, b)

    def _in_range(self, value: int) -> int:
        return min(255, max(0, value))

    @property
    def r(self) -> int:
        return self._in_range(self.x)

    @property
    def g(self) -> int:
        return self._in_range(self.y)

    @property
    def b(self) -> int:
        return self._in_range(self.z)

    def as_tuple(self):
        return self.r, self.g, self.b
