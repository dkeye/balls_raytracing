import time
from functools import lru_cache
from math import inf, sqrt
from typing import NewType, NamedTuple, Union

from PIL import Image
from PIL.ImageDraw import Draw

ACoord = NewType("ACoord", int)
BCoord = NewType("BCoord", Union[int, float])


class Vector(NamedTuple):
    x: BCoord
    y: BCoord
    z: BCoord

    def __mul__(self, other) -> int:
        return sum(BCoord(c1 * c2) for c1, c2 in zip(self, other))


class Point(NamedTuple):
    x: BCoord
    y: BCoord
    z: BCoord

    def __sub__(self, other) -> Vector:
        return Vector(*tuple(BCoord(c1 - c2) for c1, c2 in zip(self, other)))


class Sphere(NamedTuple):
    center: Point
    radius: int
    color: str


canvas_width: int = 800
canvas_height: int = 800

viewport_size: int = 1
projection_plane_z: int = 1
camera_position: Point = Point(BCoord(0), BCoord(0), BCoord(0))

BACKGROUND_COLOR: str = "white"

spheres = [
    Sphere(Point(BCoord(0), BCoord(-1), BCoord(3)), 1, "red"),
    Sphere(Point(BCoord(2), BCoord(0), BCoord(4)), 1, "blue"),
    Sphere(Point(BCoord(-2), BCoord(0), BCoord(4)), 1, "green")
]

img = Image.new(mode="RGB",
                size=(canvas_width, canvas_height),
                color=BACKGROUND_COLOR,
                )
draw = Draw(img)


# converting coordinate system
#                                                                    ^
#                                                                    | Y
#        0                             X                             |
#         +--------------------------+--->             +--------------------------+
#         |                          |                 |             |            |
#         |                          |                 |             |            |
#         |                          |              -X |             |0           |  X
#    A    |                          |      B     +------------------------------------>
#         |                          |                 |             |            |
#         |                          |                 |             |            |
#         |                          |                 |             |            |
#         +--------------------------+                 +--------------------------+
#       Y |                                                          |
#         v                                                          + -Y
#

@lru_cache(maxsize=canvas_height * canvas_width)
def encode(x: ACoord, y: ACoord) -> (BCoord, BCoord):
    """
    A to B
    width = 600
    height = 400
    encode(0, 0) == (-300, 200)
    encode(600, 400) == (300, -200)
    """
    return BCoord(-canvas_width // 2 + x), BCoord(canvas_height // 2 - y)


@lru_cache(maxsize=canvas_height * canvas_width)
def decode(x: BCoord, y: BCoord) -> (ACoord, ACoord):
    """
    B to A
    width = 600
    height = 400
    decode(-300, 200) == (0, 0)
    decode(300, -200) == (600, 400)
    """
    return ACoord(canvas_width // 2 + x), ACoord(canvas_height // 2 - y - 1)


# precompute
for xt in range(canvas_width):
    for yt in range(canvas_height):
        ACoord(xt), ACoord(yt)
        xtt, ytt = encode(ACoord(xt), ACoord(yt))
        decode(xtt, ytt)


def put_pixel(x: BCoord, y: BCoord, color: str, draw: Draw = draw) -> None:
    x, y = decode(x, y)
    if not (x < 0 or x > canvas_width or y < 0 or y > canvas_height):
        draw.point(xy=(x, y), fill=color)


def canvas_to_viewport(x: BCoord, y: BCoord, d: BCoord = BCoord(projection_plane_z)) -> Vector:
    return Vector(BCoord(x * viewport_size / canvas_width), BCoord(y * viewport_size / canvas_height), d)


def intersect_ray_sphere(origin: Point, direction_ray: Vector, sphere: Sphere) -> (float, float):
    center: Point = sphere.center
    radius: int = sphere.radius
    oc: Vector = origin - center

    k1: int = direction_ray * direction_ray
    k2: int = 2 * (oc * direction_ray)
    k3: int = oc * oc - radius * radius

    discriminant: int = k2 * k2 - 4 * k1 * k3
    if discriminant < 0:
        return inf, inf
    t1: float = (-k2 + sqrt(discriminant)) / (2 * k1)
    t2: float = (-k2 - sqrt(discriminant)) / (2 * k1)
    return t1, t2


def trace_ray(origin: Point, direction_ray: Vector, t_min: float, t_max: float):
    closest_t = t_max
    closest_sphere = None
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction_ray, sphere)
        if t1 < closest_t and t_min < t1 < t_max:
            closest_t = t1
            closest_sphere = sphere
        if t2 < closest_t and t_min < t2 < t_max:
            closest_t = t2
            closest_sphere = sphere
    if closest_sphere is None:
        return BACKGROUND_COLOR
    return closest_sphere.color


def main():
    start = time.time()

    for x in range(-canvas_width // 2, canvas_width // 2):
        x = BCoord(x)
        for y in range(-canvas_height // 2, canvas_height // 2):
            y = BCoord(y)
            direction_ray = canvas_to_viewport(x, y)
            color = trace_ray(camera_position, direction_ray, 1, inf)
            if color != BACKGROUND_COLOR:
                put_pixel(x, y, color)

    stop = time.time() - start

    draw.text(xy=(canvas_width // 3, 30), text=f"rendered in {stop} seconds", fill="black")


if __name__ == '__main__':
    main()
    img.show()
    img.save('v1.png', "png", compress_level=0)
