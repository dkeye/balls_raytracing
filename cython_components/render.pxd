from .vector cimport Vector
from .color cimport Color
from .geometry cimport Sphere
from .viewport cimport Viewport

cpdef void render_scene(screen, int canvas_width, int canvas_height, list spheres, list lights, Color background_color, Vector camera_position, int recursion_depth, Viewport viewport)

cpdef void rotate_scene(float angle, list spheres)