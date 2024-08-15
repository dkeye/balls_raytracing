from libc.math cimport sqrt, INFINITY
from .vector cimport Vector
from .color cimport Color
from cython.operator cimport dereference as deref
from cython cimport double, bint, list

cdef class Sphere:

    def __init__(self, Vector center, int radius, tuple color, int specular, double reflective):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular
        self.reflective = reflective


cdef class Light:

    def __init__(self, str type, double intensity, Vector position=None, Vector direction=None):
        self.type = type
        self.intensity = intensity
        self.position = position
        self.direction = direction


cdef inline tuple intersect_ray_sphere(Vector origin, Vector direction_ray, Sphere sphere):
    cdef Vector center = sphere.center
    cdef int radius = sphere.radius
    cdef Vector oc = origin - center

    cdef double k1 = direction_ray * direction_ray
    cdef double k2 = 2.0 * (oc * direction_ray)
    cdef double k3 = oc * oc - radius * radius

    cdef double discriminant = k2 * k2 - 4.0 * k1 * k3
    if discriminant < 0:
        return INFINITY, INFINITY

    cdef double t1 = (-k2 + sqrt(discriminant)) / (2.0 * k1)
    cdef double t2 = (-k2 - sqrt(discriminant)) / (2.0 * k1)
    return t1, t2


cdef tuple closest_intersection(Vector origin, Vector direction_ray, double t_min, double t_max, list spheres):
    cdef double closest_t = t_max
    cdef Sphere closest_sphere = None
    cdef double t1, t2

    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction_ray, sphere)
        if t_min < t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if t_min < t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere

    return closest_sphere, closest_t


cpdef Color trace_ray(Vector origin, Vector direction_ray, double t_min, double t_max, int depth, list spheres, list lights, Color background_color):
    cdef Sphere closest_sphere
    cdef double closest_t
    closest_sphere, closest_t = closest_intersection(origin, direction_ray, t_min, t_max, spheres)

    if closest_sphere is None:
        return background_color

    cdef Vector point = origin + direction_ray.scale(closest_t)
    cdef Vector normal = (point - closest_sphere.center).scale(1.0 / (point - closest_sphere.center).length())
    cdef Vector view = direction_ray.scale(-1)

    # Compute local color
    cdef double cl = compute_lighting(point, normal, view, closest_sphere.specular, lights, spheres)
    cdef Color local_color = Color(cl * closest_sphere.color[0], cl * closest_sphere.color[1], cl * closest_sphere.color[2])

    if depth <= 0 or closest_sphere.reflective <= 0:
        return local_color

    cdef Vector reflected_ray = reflect_ray(view, normal)
    cdef Color reflected_color = trace_ray(point, reflected_ray, 0.001, INFINITY, depth - 1, spheres, lights, background_color)
    cdef Vector result = (local_color.scale(1 - closest_sphere.reflective)) + (reflected_color.scale(closest_sphere.reflective))
    return Color(result.x, result.y, result.z)


cdef double compute_lighting(Vector point, Vector normal, Vector view, int specular, list lights, list spheres):
    cdef double intensity = 0.0
    cdef double length_normal = normal.length()
    cdef double t_max, n_dot_l, r_dot_v
    cdef Sphere shadow_sphere
    cdef double shadow_t

    for light in lights:
        if light.type == "ambient":
            intensity += light.intensity
        else:
            if light.type == "point":
                vec_l = light.position - point
                t_max = 1.0
            else:
                vec_l = light.direction
                t_max = INFINITY

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


cdef inline Vector reflect_ray(Vector point, Vector normal):
    return (normal.scale(2 * (normal * point))) - point
