import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 60

# Simplified level data (Y is inverted for Pygame: 0 is top)
zoo_level = [
    {"x": 100, "y": 500, "w": 600, "h": 50, "type": "block"}, # Floor
    {"x": 0,   "y": 400, "w": 200, "h": 20, "type": "block"}, # Platform
]

def create_structure(space, info):
    """Creates static physical boundaries for the level."""
    body = space.static_body
    shape = pymunk.Poly.create_box(body, (info["w"], info["h"]))
    # Pymunk uses center coordinates
    shape.body.position = (info["x"] + info["w"]/2, info["y"] + info["h"]/2)
    shape.elasticity = 0.5
    shape.friction = 0.5
    space.add(shape)
    return shape

def create_player(space, pos):
    """Creates a physics-enabled player circle."""
    mass = 1
    radius = 20
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.friction = 0.8
    space.add(body, shape)
    return shape

def getinput(player_shape):
    """Handles movement: Left, Right, and Jump."""
    keys = pygame.key.get_pressed()
    v = player_shape.body.velocity
    
    if keys[pygame.K_LEFT]:
        player_shape.body.velocity = (-200, v.y)
    elif keys[pygame.K_RIGHT]:
        player_shape.body.velocity = (200, v.y)
    else:
        player_shape.body.velocity = (0, v.y)

    # Simple Jump (only if vertical velocity is near zero)
    if keys[pygame.K_SPACE] and abs(v.y) < 0.1:
        player_shape.body.apply_impulse_at_local_point((0, -400))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Landfill Cleaner - Apps for Good")
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Physics Space
    space = pymunk.Space()
    space.gravity = (0, 900) # Gravity pulls down

    # Create Level Geometry
    for item in zoo_level:
        create_structure(space, item)

    # Create Player
    player = create_player(space, (400, 100))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. Input
        getinput(player)

        # 2. Physics Update
        dt = 1.0 / FPS
        space.step(dt)

        # 3. Drawing
        screen.fill((200, 230, 255)) # Sky Blue
        
        # Draw Platforms
        for item in zoo_level:
            pygame.draw.rect(screen, (101, 67, 33), (item["x"], item["y"], item["w"], item["h"]))
        
        # Draw Player (using pymunk helper for simplicity)
        space.debug_draw(draw_options)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
