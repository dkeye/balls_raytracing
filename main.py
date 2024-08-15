import pygame
from components import Vector, Color, Viewport
from geometry import Sphere, Light
from render import render_scene, rotate_scene

version = "6"

# Global Configuration
canvas_width = 400
canvas_height = 400
projection_plane_z = 1
camera_position = Vector(0, 0, 0)
recursion_depth = 1
BACKGROUND_COLOR = Color(0, 0, 0)

spheres = [
    Sphere(Vector(0, -1, 3), 1, (255, 0, 0), 500, 0.2),
    Sphere(Vector(1.7, 0, 4), 1, (0, 0, 255), 500, 0.3),
    Sphere(Vector(-1.8, 0, 4), 1, (0, 255, 0), 10, 0.4),
    Sphere(Vector(0, -5001, 0), 5000, (255, 255, 0), 1000, 0.1),
]

lights = [
    Light(type="ambient", intensity=0.2),
    Light(type="point", intensity=0.6, position=Vector(2, 1, 0)),
    Light(type="directional", intensity=0.2, direction=Vector(1, 4, 4)),
]

viewport = Viewport(width=1, height=1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((canvas_width, canvas_height))
    pygame.display.set_caption(f"Ray Tracer v{version}")

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    rotation_angle = 0
    rotate_left = True
    max_angle = 10
    running = True

    while running:
        start_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if abs(rotation_angle) >= max_angle:
            rotate_left = not rotate_left
        rotation_angle = rotation_angle - 0.1 if rotate_left else rotation_angle + 0.1
        rotate_scene(rotation_angle, spheres)

        screen.fill(BACKGROUND_COLOR.as_tuple())
        render_scene(screen, canvas_width, canvas_height, spheres, lights, BACKGROUND_COLOR, camera_position, recursion_depth, viewport)

        frame_time = pygame.time.get_ticks() - start_time
        if frame_time > 0:
            fps = 1000.0 / frame_time

        fps_text = font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
