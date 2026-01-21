import os.path
import argparse

import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import pymunk.bb

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
args = parser.parse_args()
debug = False
if args.debug:
    debug = True
# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 120

def getimg(name):
    return pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), name))

# Simplified level data (Y is inverted for Pygame: 0 is top)
zoo_level = [
    {"x": 100, "y": 500, "w": 600, "h": 50, "type": "block"}, # Floor
    {"x": 0,   "y": 400, "w": 300, "h": 50, "type": "block"}, # Platform
    {"x": 50,  "y": 450, "w": 300, "h": 50, "type": "block"}, # Step
    {"x": 0,   "y": 350, "w": 300, "h": 50, "type": "block"}, # Roof
]
#bottle_img = getimg("bottle.png")


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
    moment = pymunk.moment_for_poly(mass, [(-10,0), (0, -10), (10, 0), (0,10)])
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Poly(body, [(-10,0), (0, -10), (10, 0), (0,10)])
    shape.friction = 0.8
    space.add(body, shape)
    return shape

# Simplified level data (Y is inverted for Pygame: 0 is top)
zoo_level = [
    {"x": 100, "y": 500, "w": 600, "h": 50, "type": "block"}, # Floor
    {"x": 0,   "y": 400, "w": 300, "h": 50, "type": "block"}, # Platform
    {"x": 50,  "y": 450, "w": 300, "h": 50, "type": "block"}, # Step
    {"x": 0,   "y": 350, "w": 300, "h": 50, "type": "block"}, # Roof
]

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
    if keys[pygame.K_UP] and abs(v.y) < 0.1:
        player_shape.body.velocity = (v.x, -400)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Landfill Cleaner - Apps for Good")
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Physics Space
    space = pymunk.Space()
    space.gravity = (0,950) # Gravity pulls down

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

        # if player out of bounds, reset 
        if player.body.position.y > HEIGHT:
            player.body.position = (400, 100)
            player.body.velocity = (0, 0)
            player.body.angular_velocity = 0
            player.body.angle = 0

        # 2. Physics Update
        dt = 0.01 / FPS
        for i in range(100):
            space.step(dt)
    # 3. Drawing
        # Calculate camera offset to center the player
        camera_offset = Vec2d(WIDTH / 2 - player.body.position.x, HEIGHT / 2 - player.body.position.y)

        screen.fill((200, 230, 255)) # Sky Blue

        # Draw Platforms with camera offset
        for item in zoo_level:
            pygame.draw.rect(screen, (101, 67, 33), (item["x"] + camera_offset.x, item["y"] + camera_offset.y, item["w"], item["h"]))

        # Display fps
        fps_text = "FPS: " + str(int(clock.get_fps()))
        y = 5
        font = pygame.font.Font(None, 16)
        text = font.render(fps_text, True, pygame.Color("black"))
        screen.blit(text, (5, y))

        # Draw Player with camera offset
        # Draw the player polygon manually since debug_draw doesn't support easy offsetting
        player_pos = player.body.position + camera_offset
        points = []
        for v in player.get_vertices():
            # Rotate vertex
            v_rotated = v.rotated(player.body.angle)
            # Offset and translate
            points.append((v_rotated.x + player_pos.x, v_rotated.y + player_pos.y))
        pygame.draw.polygon(screen, (255, 0, 0), points)

        # screen.blit(bottle_img, player_pos - Vec2d(17,20))

        if debug == True:
            # Note: debug_draw might not look right with camera offset unless we transform the draw options
            # For now, we'll just skip it or keep it static
            space.debug_draw(draw_options)

        pygame.display.flip()
        clock.tick(FPS)
        fps = str(clock.get_fps())

    pygame.quit()

if __name__ == "__main__":
    main()
