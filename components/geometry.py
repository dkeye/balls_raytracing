from math import sqrt
from typing import Optional, Tuple

from cython_components import Color, Vector


class Sphere:
    def __init__(self, center: Vector, radius: int, color: Tuple[int, int, int], specular: int, reflective: float):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular
        self.reflective = reflective


class Light:
    def __init__(self, type: str, intensity: float, position: Optional[Vector] = None, direction: Optional[Vector] = None):
        self.type = type
        self.intensity = intensity
        self.position = position
        self.direction = direction


def intersect_ray_sphere(origin: Vector, direction_ray: Vector, sphere: Sphere) -> Tuple[float, float]:
    center = sphere.center
    radius = sphere.radius
    oc = origin - center

    k1 = direction_ray * direction_ray
    k2 = 2 * (oc * direction_ray)
    k3 = oc * oc - radius * radius

    discriminant = k2 * k2 - 4 * k1 * k3
    if discriminant < 0:
        return float('inf'), float('inf')

    t1 = (-k2 + sqrt(discriminant)) / (2 * k1)
    t2 = (-k2 - sqrt(discriminant)) / (2 * k1)
    return t1, t2


def closest_intersection(origin: Vector, direction_ray: Vector, t_min: float, t_max: float, spheres: list[Sphere]) -> Tuple[Optional[Sphere], float]:
    closest_t = t_max
    closest_sphere = None

    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction_ray, sphere)
        if t_min < t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if t_min < t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere

    return closest_sphere, closest_t


def trace_ray(origin: Vector, direction_ray: Vector, t_min: float, t_max: float, depth: int, spheres: list[Sphere], lights: list[Light], background_color: Color) -> Color:
    closest_sphere, closest_t = closest_intersection(origin, direction_ray, t_min, t_max, spheres)

    if closest_sphere is None:
        return background_color

    point = origin + direction_ray.scale(closest_t)
    normal = (point - closest_sphere.center) ** (1 / (point - closest_sphere.center).length())
    view = direction_ray ** -1

    # Compute local color
    cl = compute_lighting(point, normal, view, closest_sphere.specular, lights, spheres)
    local_color = Color(cl * closest_sphere.color[0], cl * closest_sphere.color[1], cl * closest_sphere.color[2])

    if depth <= 0 or closest_sphere.reflective <= 0:
        return local_color

    reflected_ray = reflect_ray(view, normal)
    reflected_color = trace_ray(point, reflected_ray, 0.001, float('inf'), depth - 1, spheres, lights, background_color)
    result = (local_color.scale(1 - closest_sphere.reflective)) + (reflected_color.scale(closest_sphere.reflective))
    return Color(result.x, result.y, result.z)


def compute_lighting(point: Vector, normal: Vector, view: Vector, specular: int, lights: list[Light], spheres: list[Sphere]) -> float:
    intensity = 0.0
    length_normal = normal.length()

    for light in lights:
        if light.type == "ambient":
            intensity += light.intensity
        else:
            if light.type == "point":
                vec_l = light.position - point
                t_max = 1
            else:
                vec_l = light.direction
                t_max = float('inf')

            shadow_sphere, shadow_t = closest_intersection(point, vec_l, 0.001, t_max, spheres)
            if shadow_sphere is not None:
                continue

            n_dot_l = normal * vec_l
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (length_normal * vec_l.length())

            if specular != -1:
                vec_r = reflect_ray(vec_l, normal)
                r_dot_v = vec_r * view
                if r_dot_v > 0:
                    intensity += light.intensity * ((r_dot_v / (vec_r.length() * view.length())) ** specular)

    return intensity


def reflect_ray(point: Vector, normal: Vector) -> Vector:
    return (normal ** (2 * (normal * point))) - point
