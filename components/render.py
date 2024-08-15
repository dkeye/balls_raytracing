from components import Vector, Color, Viewport
from geometry import Sphere, trace_ray


def decode(x: int, y: int, canvas_width: int, canvas_height: int) -> (int, int):
    return canvas_width // 2 + x, canvas_height // 2 - y - 1


def put_pixel(x: int, y: int, color: Color, screen, canvas_width: int, canvas_height: int) -> None:
    x, y = decode(x, y, canvas_width, canvas_height)
    if 0 <= x < canvas_width and 0 <= y < canvas_height:
        screen.set_at((x, y), color.as_tuple())


def canvas_to_viewport(x: int, y: int, viewport: Viewport, canvas_width: int, canvas_height: int, d: int = 1) -> Vector:
    return Vector(x * viewport.width / canvas_width, y * viewport.height / canvas_height, d)


def rotate_scene(angle: float, spheres: list[Sphere]):
    for i, sphere in enumerate(spheres):
        spheres[i].center = sphere.center.rotate_y(angle)


def render_scene(screen, canvas_width: int, canvas_height: int, spheres, lights, background_color, camera_position: Vector, recursion_depth: int, viewport: Viewport):
    for x in range(-canvas_width // 2, canvas_width // 2):
        for y in range(-canvas_height // 2, canvas_height // 2):
            direction_ray = canvas_to_viewport(x, y, viewport, canvas_width, canvas_height)
            color = trace_ray(camera_position, direction_ray, 1, float('inf'), recursion_depth, spheres, lights, background_color)
            if color != background_color:
                put_pixel(x, y, color, screen, canvas_width, canvas_height)
