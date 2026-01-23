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
bottle_collect_dist = 20
playerdirection = False

def getimg(name):
    return pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), name))

# Simplified level data (Y is inverted for Pygame: 0 is top)
zoo_level = [
    {"x": 100, "y": 500, "w": 600, "h": 50, "type": "block"}, # Floor
    {"x": 0,   "y": 400, "w": 300, "h": 50, "type": "block"}, # Platform
    {"x": 50,  "y": 450, "w": 300, "h": 50, "type": "block"}, # Step
    {"x": 0,   "y": 300, "w": 300, "h": 50, "type": "block"}, # Roof
    {"x": 428, "y": 350, "w": 75,  "h": 50, "type": "block"}, # platforming block
]
bottle_img = getimg("bottle.png")
player_img = getimg("player.png")
player_reversed_img = getimg("player_reversed.png")


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
    player_shape = [(11, 22), (-11, 22), (-11, -13), (11, -13)]
    mass = 1
    moment = pymunk.moment_for_poly(mass, player_shape)
    body = pymunk.Body(mass, moment)
    body.position = pos
    body.angle = 0
    shape = pymunk.Poly(body, player_shape)
    shape.friction = 0.8
    space.add(body, shape)
    return shape

def getinput(player_shape, isreversed):
    """Handles movement: Left, Right, and Jump."""
    keys = pygame.key.get_pressed()
    v = player_shape.body.velocity
    player_shape.body.angle = 0
    
    if keys[pygame.K_LEFT]:
        player_shape.body.velocity = (-200, v.y)
        isreversed = True
    elif keys[pygame.K_RIGHT]:
        player_shape.body.velocity = (200, v.y)
        isreversed = False
    else:
        player_shape.body.velocity = (0, v.y)

    # Simple Jump (only if vertical velocity is near zero)
    if keys[pygame.K_UP] and abs(v.y) < 0.2:
        player_shape.body.velocity = (v.x, -400)
        player_shape.body.angle = 0 
    elif keys[pygame.K_f]:
        print("VEL: " + str(player_shape.body.velocity) +  " POS: " + str(player_shape.body.position) + " ANGLE: " + str(player_shape.body.angle))
    return isreversed

def create_bottle(space, pos: Vec2d):
    """Creates a physics-enabled bottle."""
    mass = 1
    bottle_shape = [(-10,0), (0, -10), (10, 0), (0,10)]
    moment = pymunk.moment_for_poly(mass, bottle_shape)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Poly(body, bottle_shape)
    shape.friction = 0.8
    space.add(body, shape)
    return shape

def create_bottles(space):
    """Creates bottles in the level."""
    bottles = []
    bottle_x = [50, 60, 70, 80, 90, 100, 110, 120]
    for i in range(len(bottle_x)):
        bottles.append(create_bottle(space, (bottle_x[i], 200)))
    return bottles

def main(playerdirection):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Landfill Cleaner - Apps for Good")
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    bottles_collected = 0

    # Physics Space
    space = pymunk.Space()
    space.gravity = (0, 950) # Gravity pulls down

    # Create Level Geometry
    for item in zoo_level:
        create_structure(space, item)

    # Create Player
    player = create_player(space, (400, 100))
    items = create_bottles(space)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. Input
        playerdirection = getinput(player, playerdirection)

        # if player out of bounds, reset
        if player.body.position.y > HEIGHT:
            print("Player velocity: ", player.body.velocity)
            print("Player angular velocity: ", player.body.angular_velocity)
            print("Player angle: ", player.body.angle)
            player.body.position = (400, 488)
            player.body.velocity = (0, 0)
            player.body.angular_velocity = 0
            player.body.angle = 0
            print("Player fell out of the world!")
            print("Resetting player to (400, 488)")
            print("Player velocity: ", player.body.velocity)
            print("Player angular velocity: ", player.body.angular_velocity)
            print("Player angle: ", player.body.angle)

        # 2. Physics Update
        num = 150
        phy = (1/num)
        dt = phy / FPS
        for i in range(num):
            player.body.angle = 0
            space.step(dt)
            player.body.angle = 0
        # 3. Drawing
        screen.fill((200, 230, 255)) # Sky Blue

        # Draw Platforms
        for item in zoo_level:
            pygame.draw.rect(screen, (101, 67, 33), (item["x"], item["y"], item["w"], item["h"]))

        # Display fps
        fps = "FPS: " + str(int(clock.get_fps()))
        bottles_gotten = "Bottles Collected: " + str(bottles_collected)
        y = 5
        font = pygame.font.Font(None, 16)
        bottle_text = font.render(bottles_gotten, True, pygame.Color("black"))
        text = font.render(fps, True, pygame.Color("black"))
        screen.blit(text, (5, y))
        screen.blit(bottle_text, (5, y+10))

        if playerdirection:
            screen.blit(player_reversed_img, player.body.position-Vec2d(17,10))
        else:
            screen.blit(player_img, player.body.position-Vec2d(17,10))

        for item in items:
            if item.body.position.y > HEIGHT:
                space.remove(item.body, item)
                items.remove(item)
            elif item.body.position.x <= player.body.position.x+bottle_collect_dist and item.body.position.x >= player.body.position.x-bottle_collect_dist and item.body.position.y <= player.body.position.y+bottle_collect_dist and item.body.position.y >= player.body.position.y-bottle_collect_dist:
                space.remove(item.body, item)
                items.remove(item)
                print("Bottle collected!")
                bottles_collected = bottles_collected + 1
            else:
                screen.blit(bottle_img, item.body.position-Vec2d(17,20))

        # Draw Player (using pymunk helper for simplicity)
        if debug:
            space.debug_draw(draw_options)

        pygame.display.flip()
        clock.tick(FPS)
        fps = str(clock.get_fps())

    pygame.quit()

if __name__ == "__main__":
    main(playerdirection)

