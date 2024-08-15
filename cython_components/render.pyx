from .vector cimport Vector
from .color cimport Color
from .geometry cimport Sphere, trace_ray
from .viewport cimport Viewport
from libc.math cimport INFINITY

cdef inline tuple decode(int x, int y, int canvas_width, int canvas_height):
    return canvas_width // 2 + x, canvas_height // 2 - y - 1

cdef inline void put_pixel(int x, int y, Color color, screen, int canvas_width, int canvas_height):
    cdef int dx, dy
    dx, dy = decode(x, y, canvas_width, canvas_height)
    if 0 <= dx < canvas_width and 0 <= dy < canvas_height:
        screen.set_at((dx, dy), color.as_tuple())

cdef inline Vector canvas_to_viewport(int x, int y, Viewport viewport, int canvas_width, int canvas_height, int d=1):
    return Vector(x * viewport.width / canvas_width, y * viewport.height / canvas_height, d)

cpdef void rotate_scene(float angle, list spheres):
    for i in range(len(spheres)):
        spheres[i].center = spheres[i].center.rotate_y(angle)

cpdef void render_scene(screen, int canvas_width, int canvas_height, list spheres, list lights, Color background_color, Vector camera_position, int recursion_depth, Viewport viewport):
    cdef int x, y
    cdef Vector direction_ray
    cdef Color color
    for x in range(-canvas_width // 2, canvas_width // 2):
        for y in range(-canvas_height // 2, canvas_height // 2):
            direction_ray = canvas_to_viewport(x, y, viewport, canvas_width, canvas_height)
            color = trace_ray(camera_position, direction_ray, 1, INFINITY, recursion_depth, spheres, lights, background_color)
            if color != background_color:
                put_pixel(x, y, color, screen, canvas_width, canvas_height)
