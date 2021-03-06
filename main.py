from __future__ import annotations

import time
from functools import lru_cache
from math import inf, sqrt
from typing import NamedTuple, Union, Optional

from PIL import Image, ImageFont
from PIL.ImageDraw import Draw

version = "5,5"


class Vector(NamedTuple):
    x: Union[int, float]
    y: Union[int, float]
    z: Union[int, float]

    def __mul__(self, other: Vector) -> int:
        """Dot product of two 3D vectors."""
        return self[0] * other[0] + self[1] * other[1] + self[2] * other[2]

    def __pow__(self, power: Union[float, int]) -> Vector:
        """Computes k * vec"""
        return Vector(self[0] * power, self[1] * power, self[2] * power)

    def __rpow__(self, power):
        """Computes k * vec"""
        return self.__pow__(power)

    def __sub__(self, other: Vector) -> Vector:
        """Computes v1 - v2"""
        return Vector(self[0] - other[0], self[1] - other[1], self[2] - other[2])

    def __add__(self, other: Vector) -> Vector:
        """Computes v1 + v2"""
        return Vector(self[0] + other[0], self[1] + other[1], self[2] + other[2])

    def __len__(self):
        """Length of a 3D vector."""
        return sqrt(self.__mul__(self))


# print(Vector(1, 1, 1) ** 3)
# print(3 ** Vector(1, 1, 1))
# exit()


class Sphere(NamedTuple):
    center: Vector
    radius: int
    color: tuple
    specular: int
    reflective: float


class Light(NamedTuple):
    type: str
    intensity: float
    position: Vector = None
    direction: Vector = None


canvas_width: int = 400
canvas_height: int = 400

viewport_size: int = 1


class Viewport(NamedTuple):
    width: int = 1
    height: int = 1


viewport = Viewport()

projection_plane_z: int = 1
camera_position: Vector = Vector(0, 0, 0)
recursion_depth = 3

BACKGROUND_COLOR: Vector = Vector(0, 0, 0)

spheres = [
    Sphere(
        Vector(0, -1, 3),
        1,
        (255, 0, 0),
        500,
        0.2
    ),
    Sphere(
        Vector(1.7, 0, 4),
        1,
        (0, 0, 255),
        500,
        0.3
    ),
    Sphere(
        Vector(-1.8, 0, 4),
        1,
        (0, 255, 0),
        10,
        0.4
    ),
    Sphere(
        Vector(0, -5001, 0),
        5000,
        (255, 255, 0),
        1000,
        0.1
    ),
]

lights = [
    Light(type="ambient", intensity=0.2),
    Light(type="point", intensity=0.6, position=Vector(2, 1, 0)),
    Light(type="directional", intensity=0.2, direction=Vector(1, 4, 4)),
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
def encode(x: int, y: int) -> (int, int):
    """
    A to B
    width = 600
    height = 400
    encode(0, 0) == (-300, 200)
    encode(600, 400) == (300, -200)
    """
    return -canvas_width // 2 + x, canvas_height // 2 - y


@lru_cache(maxsize=canvas_height * canvas_width)
def decode(x: int, y: int) -> (int, int):
    """
    B to A
    width = 600
    height = 400
    decode(-300, 200) == (0, 0)
    decode(300, -200) == (600, 400)
    """
    return canvas_width // 2 + x, canvas_height // 2 - y - 1


# precompute
for xt in range(canvas_width):
    for yt in range(canvas_height):
        xtt, ytt = encode(xt, yt)
        decode(xtt, ytt)


def put_pixel(x: int, y: int, color: Vector, draw: Draw = draw) -> None:
    x, y = decode(x, y)
    if not (x < 0 or x > canvas_width or y < 0 or y > canvas_height):
        color = int(color[0]), int(color[1]), int(color[2])
        draw.point(xy=(x, y), fill=color)


def canvas_to_viewport(x: int, y: int, d: int = projection_plane_z) -> Vector:
    return Vector(x * viewport.width / canvas_width, y * viewport.height / canvas_height, d)


def reflect_ray(point: Vector, normal: Vector) -> Vector:
    return (normal ** (2 * (normal * point))) - point


def compute_lighting(point: Vector, normal: Vector, view: Vector, specular: int) -> float:
    i = 0.0
    length_normal = normal.__len__()
    for light in lights:
        if light.type == "ambient":
            i += light.intensity
        else:
            if light.type == "point":
                vec_l: Vector = light.position - point
                t_max = 1
            else:
                vec_l: Vector = light.direction
                t_max = inf

            # Shadow check
            shadow_sphere, shadow_t = closest_intersection(point, vec_l, 0.001, t_max)
            if shadow_sphere is not None:
                continue

            # Diffuse
            n_dot_l: float = normal * vec_l
            if n_dot_l > 0:
                i += light.intensity * n_dot_l / (length_normal * vec_l.__len__())

            # Specular
            if specular != -1:
                vec_r: Vector = reflect_ray(vec_l, normal)
                r_dot_v: float = vec_r * view
                if r_dot_v > 0:
                    i += light.intensity * ((r_dot_v / (vec_r.__len__() * view.__len__())) ** specular)

    return i


def intersect_ray_sphere(origin: Vector, direction_ray: Vector, sphere: Sphere) -> (float, float):
    center: Vector = sphere.center
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


def closest_intersection(origin: Vector, direction_ray: Vector, t_min: float, t_max: float) -> (Sphere, float):
    closest_t: float = t_max
    closest_sphere: Optional[Sphere] = None
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction_ray, sphere)
        if t1 < closest_t and t_min < t1 < t_max:
            closest_t = t1
            closest_sphere = sphere
        if t2 < closest_t and t_min < t2 < t_max:
            closest_t = t2
            closest_sphere = sphere
    return closest_sphere, closest_t


def trace_ray(origin: Vector, direction_ray: Vector, t_min: float, t_max: float, depth: int) -> Vector:
    closest_sphere, closest_t = closest_intersection(origin, direction_ray, t_min, t_max)
    if closest_sphere is None:
        return BACKGROUND_COLOR

    # Compute local color
    point: Vector = origin + closest_t ** direction_ray
    normal: Vector = point - closest_sphere.center
    normal: Vector = (1 / normal.__len__()) ** normal
    view: Vector = direction_ray ** -1
    cl = compute_lighting(point, normal, view, closest_sphere.specular)
    local_color: Vector = Vector(cl * closest_sphere.color[0], cl * closest_sphere.color[1], cl * closest_sphere.color[2])

    # If we hit the recursion limit or the object is not reflective, we're done
    r: float = closest_sphere.reflective
    if depth <= 0 or r <= 0:
        return local_color

    # Compute the reflected color
    reflected_ray: Vector = reflect_ray(view, normal)
    reflected_color: Vector = trace_ray(point, reflected_ray, 0.001, inf, depth - 1)
    return ((1 - r) ** local_color) + (r ** reflected_color)


def main():
    start = time.time()

    for x in range(-canvas_width // 2, canvas_width // 2):
        for y in range(-canvas_height // 2, canvas_height // 2):
            direction_ray = canvas_to_viewport(x, y)
            color = trace_ray(camera_position, direction_ray, 1, inf, recursion_depth)
            if color != BACKGROUND_COLOR:
                put_pixel(x, y, color)

    stop = time.time() - start

    font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 12)

    draw.text(
        xy=(canvas_width // 3, 15),
        text=f"v{version}\nrendered in {stop:.3f} seconds",
        fill="white",
        align="center",
        font=font,
    )


if __name__ == '__main__':
    main()
    img.show()
    # img.save(f'v{version}.png', "png", compress_level=0)
