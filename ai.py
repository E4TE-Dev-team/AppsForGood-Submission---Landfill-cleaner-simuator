import os.path
import argparse
import random
import enum
# import math

import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Poly, Vec2d
import pymunk.bb

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
args = parser.parse_args()
debug = False
random.seed(0)
if args.debug:
    debug = True

class trashtypes(enum.Enum):
    BOTTLE = 1
    RUSTYMETAL = 2

class Struct:
    type = trashtypes.BOTTLE
    shape: Poly
    pass
    

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 120
bottle_collect_dist = 20
shop_open = False
playerdirection = False

def getimg(name):
    return pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), name))

# Simplified level data (Y is inverted for Pygame: 0 is top)
zoo_level = [
    {"x": 100, "y": 500, "w": 600, "h": 50, "type": "block"}, # Floor
    {"x": 0,   "y": 400, "w": 300, "h": 50, "type": "block"}, # Platform
    {"x": 50,  "y": 450, "w": 300, "h": 50, "type": "block"}, # Step
    {"x": 0,   "y": 275, "w": 300, "h": 50, "type": "block"}, # Roof
    {"x": 428, "y": 350, "w": 75,  "h": 50, "type": "block"}, # platforming block
    {"x": 500, "y": 300, "w": 75,  "h": 50, "type": "block"}, # platforming block
]
try:
    bottle_img = getimg("bottle.png")
except FileNotFoundError:
    print("404: Bottle image not found.")
    bottle_img = pygame.Surface((34, 40))
try:
    rustymetal_img = getimg("rustymetal.png")
except FileNotFoundError:
    print("404: Rusty metal image not found.")
    rustymetal_img = pygame.Surface((34, 40))
try:
    player_img = getimg("player.png")
except FileNotFoundError:
    print("404: Player image not found.")
    player_img = pygame.Surface((34, 34))
try:
    player_reversed_img = getimg("player_reversed.png")
except FileNotFoundError:
    print("404: Player reversed image not found.")
    player_reversed_img = pygame.Surface((34, 34))



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
    twashstruct = Struct()
    twashstruct.type = trashtypes.BOTTLE
    twashstruct.shape = shape
    return twashstruct

def create_plate(space, pos: Vec2d):
    mass = 1
    bottle_shape = [(-10,0), (0, -10), (10, 0), (0,10)]
    moment = pymunk.moment_for_poly(mass, bottle_shape)
    body = pymunk.Body(mass, moment)
    body.position = pos
    shape = pymunk.Poly(body, bottle_shape)
    shape.friction = 0.8
    space.add(body, shape)
    twashstruct = Struct()
    twashstruct.type = trashtypes.RUSTYMETAL
    twashstruct.shape = shape
    return twashstruct

def physics(player, space, clock):
    """Updates the physics simulation."""
    num = 150
    phy = (1/num)
    try:
        dt = phy / int(clock.get_fps())
    except ZeroDivisionError:
        dt = phy / FPS
    for i in range(num):
        player.body.angle = 0
        space.step(dt)
        player.body.angle = 0

def create_twash(space):
    """Creates bottles in the level."""
    bottles = []
    bottle_x = []
    for b in range(5):
        bottle_x.append(random.randint(50, 180))


    for i in range(len(bottle_x)):
        if random.randint(1, 2) == 1:
            bottles.append(create_bottle(space, (bottle_x[i], 200)))
        elif random.randint(1, 2) == 2:
            bottles.append(create_plate(space, (bottle_x[i], 200)))
    return bottles

def generateWhiteNoise(width,height):
    noise = [[r for r in range(width)] for i in range(height)]

    for i in range(0,height):
        for j in range(0,width):
            noise[i][j] = random.randint(0,4)

    return noise

def twashthead(items, space):
    type = random.randint(1, 2)
    if type == 1:
        items.append(create_bottle(space, (random.randint(50, 180), 200)))
    elif type == 2:
        items.append(create_plate(space, (random.randint(50, 180), 200)))
        

def main(playerdirection):
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Landfill Cleaner - Apps for Good")
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    bottles_collected = 0
    shop_open = False

    # Physics Space
    space = pymunk.Space()
    space.gravity = (0, 950) # Gravity pulls down

    
    

    # Create Level Geometry
    for item in zoo_level:
        create_structure(space, item)

    

    # Create Player
    player = create_player(space, (400, 100))
    items = create_twash(space)

    last_grounded_time = 0
    coyote_time = 0.15
    jump_velocity = -400
    is_jumping = False
    
    running = True
    while running:
        current_time = pygame.time.get_ticks() /1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # bottle spawning everyb 2 sec code:
        
        
        

        
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

 
        v = player.body.velocity
        if abs(v.y) < 0.5:
            last_grounded_time = current_time
            is_jumping = False

        keys = pygame.key.get_pressed()

        if pygame.time.get_ticks() % 400 == 0:
            twashthead(items, space)

        if keys[pygame.K_f]:
            if shop_open:
                shop_open = False
            else:
                shop_open = True 

        # Jump logic: Coyote time and Variable jump height
        if keys[pygame.K_UP]:
            if current_time - last_grounded_time < coyote_time and not is_jumping:
                player.body.velocity = (v.x, jump_velocity)
                is_jumping = True
        else:
            # If button released while rising, cut vertical velocity to allow short jumps
            if is_jumping and v.y < -100:
                player.body.velocity = (v.x, -100)
                is_jumping = False

        # 2. Physics Update
        physics(player, space, clock)
        # 3. Drawing
        camera_offset = Vec2d(WIDTH / 2 - player.body.position.x, HEIGHT / 2 - player.body.position.y)

        if not shop_open: 
        
            screen.fill((200, 230, 255)) # Sky Blue

            # Draw Platforms
            for item in zoo_level:
                pygame.draw.rect(screen, (101, 67, 33), (item["x"] + camera_offset.x, item["y"] + camera_offset.y, item["w"], item["h"]))
            
            if playerdirection:
                screen.blit(player_reversed_img, (player.body.position-Vec2d(17,10))+camera_offset)
            else:
                screen.blit(player_img, (player.body.position-Vec2d(17,10))+camera_offset)

            for item in items:
                if item.shape.body.position.y > HEIGHT:
                    space.remove(item.shape.body, item.shape)
                    items.remove(item)
                elif item.shape.body.position.x <= player.body.position.x+bottle_collect_dist and item.shape.body.position.x >= player.body.position.x-bottle_collect_dist and item.shape.body.position.y <= player.body.position.y+bottle_collect_dist and item.shape.body.position.y >= player.body.position.y-bottle_collect_dist:
                    space.remove(item.shape.body, item.shape)
                    items.remove(item)
                    print("Bottle collected!")
                    bottles_collected = bottles_collected + 1
                else:
                    if item.type == trashtypes.BOTTLE:
                        screen.blit(bottle_img, (item.shape.body.position-Vec2d(17,20))+camera_offset)
                    elif item.type == trashtypes.RUSTYMETAL:
                        screen.blit(rustymetal_img, (item.shape.body.position-Vec2d(17,20))+camera_offset)

            # Draw Player (using pymunk helper for simplicity)
            if debug:
                space.debug_draw(draw_options)

        elif shop_open:
            screen.fill((255, 255, 255))
            pygame.draw.rect(screen, (101, 67, 33), (100, 100, 600, 400))
            pygame.draw.rect(screen, (101, 67, 33), (150, 150, 500, 300))
            pygame.draw.rect(screen, (101, 67, 33), (200, 200, 400, 200))
            pygame.draw.rect(screen, (101, 67, 33), (250, 250, 300, 100))
            pygame.draw.rect(screen, (101, 67, 33), (300, 300, 200, 50))
            

        # Display fps
        fps = "FPS: " + str(int(clock.get_fps()))
        bottles_gotten = "Bottles Collected: " + str(bottles_collected)
        y = 5
        font = pygame.font.Font(None, 16)
        bottle_text = font.render(bottles_gotten, True, pygame.Color("black"))
        text = font.render(fps, True, pygame.Color("black"))
        screen.blit(text, (5, y))
        screen.blit(bottle_text, (5, y+10))

        pygame.display.flip()
        clock.tick(FPS)
        fps = str(clock.get_fps())

    pygame.quit()

if __name__ == "__main__":
    # executor = ThreadPoolExecutor(max_workers=1)
    # executor.submit(main, playerdirection)
    # executor.shutdown(wait=True)
    # print("Done!")
    #      p = mp.Process(target=main, args=(playerdirection,))
    main(playerdirection)
    #      p.start()
    #      p.join()