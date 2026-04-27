#Upgrades:Better conversion rate for the coins, better items(new items)

#Things to add: Add the shop, add the max items (limit the amount of items that can spawn), better framerate/optimization*, working shop, make conversion rate an upgradable thing

#------WARNING------
# I redid the rendering code so shop no work



import os.path
import argparse
import random
import enum
import time
import concurrent.futures
import requests
#import math

import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Poly, Vec2d
import pymunk.bb

import textbox
import delay
import animation

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="debug mode", action="store_true")
parser.add_argument("-u", "--username", help="Your username")
parser.add_argument("-p", "--password", help="Your password")
args = parser.parse_args()
debug = False
random.seed(0)
if args.debug:
    debug = True


class trashtypes(enum.Enum):
    BOTTLE = 1
    RUSTYMETAL = 2
    SODA = 3


class upgradetypes(enum.Enum):
    INCREMENT = 1
    DECREMENT = 2
    REDEFINE = 3
    NONE = 4


class Struct:
    type = trashtypes.BOTTLE
    shape: Poly
    pass


class Mouse:
    x = 0
    y = 0
    pass

# Configuration
WIDTH, HEIGHT = 800, 600
FPS = 120
bottle_collect_dist = 20
shop_open = False
playerdirection = False
playerspeed = 200

def checksqlserver():
    try:
        requests.get("https://localhost:8080")
        return True
    except requests.exceptions.ConnectionError:
        return False

def create_account(username, password, score, id):
    if checksqlserver():
        requests.post("https://localhost:8080", data=f"INSERT INTO accounts (username, password, score, id) VALUES ('{username}', '{password}', {score},{id})")

def get_account(username, password):
    if checksqlserver():
        out = requests.post("https://localhost:8080", data=f"SELECT * FROM accounts WHERE username = '{username}' AND password = '{password}'")
        print(out)



def getimg(name):
    return pygame.image.load(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), name))


# Simplified level data (Y is inverted for Pygame: 0 is top)
zoo_level = [
    {
        "x": 100,
        "y": 500,
        "w": 600,
        "h": 50,
        "type": "block"
    },  # Floor
    {
        "x": 0,
        "y": 400,
        "w": 300,
        "h": 50,
        "type": "block"
    },  # Platform
    {
        "x": 50,
        "y": 450,
        "w": 300,
        "h": 50,
        "type": "block"
    },  # Step
    {
        "x": 0,
        "y": 275,
        "w": 300,
        "h": 50,
        "type": "block"
    },  # Roof
    {
        "x": 428,
        "y": 350,
        "w": 75,
        "h": 50,
        "type": "block"
    },  # platforming block
    {
        "x": 500,
        "y": 300,
        "w": 75,
        "h": 50,
        "type": "block"
    },  # platforming block
]

player_size = (45, 34)

try:
    bottle_img = getimg("AFG/Bottle_texture.png")
except FileNotFoundError:
    print("404: Bottle image not found.")
    bottle_img = pygame.Surface((34, 40))
try:
    rustymetal_img = getimg("AFG/rustymetal.png")
except FileNotFoundError:
    print("404: Rusty metal image not found.")
    rustymetal_img = pygame.Surface((34, 40))
try:
    soda_img = getimg("AFG/soda_cup.png")
except FileNotFoundError:
    print("404: Soda image not found.")
    soda_img = pygame.Surface((34, 40))
try:
    player_img_large = getimg("AFG/character_true_sprite_gaster/chara_idle.png")
except FileNotFoundError:
    print("404: Player image not found.")
    player_img_large = pygame.Surface((34, 34))
try:
    shop_notscaled = getimg("AFG/SHOP.png")
except FileNotFoundError:
    print("404: Shop image not found.")
    shop_notscaled = pygame.Surface((34, 34))

try:
    player_walk_1 = pygame.transform.scale(getimg("AFG/character_true_sprite_gaster/chara_walk_1.png"), (45, 34))
    player_walk_2 = pygame.transform.scale(getimg("AFG/character_true_sprite_gaster/chara_walk_2.png"), (45, 34))
    player_walk_3 = pygame.transform.scale(getimg("AFG/character_true_sprite_gaster/chara_walk_3.png"), (45, 34))
    player_walk_4 = pygame.transform.scale(getimg("AFG/character_true_sprite_gaster/chara_walk_4.png"), (45, 34))
    player_walk_5 = pygame.transform.scale(getimg("AFG/character_true_sprite_gaster/chara_walk_5.png"), (45, 34))
except FileNotFoundError:
    player_walk_1 = pygame.Surface((45, 34))
    player_walk_2 = pygame.Surface((45, 34))
    player_walk_3 = pygame.Surface((45, 34))
    player_walk_4 = pygame.Surface((45, 34))
    player_walk_5 = pygame.Surface((45, 34))

bottle_large_img = pygame.transform.scale(bottle_img, (100, 100))
shop_img = pygame.transform.scale(shop_notscaled, (600, 400))
player_img = pygame.transform.scale(player_img_large, (45, 34))
player_reversed_img = pygame.transform.flip(player_img, True, False)

player_reversed_walk_1 = pygame.transform.flip(player_walk_1, True, False)
player_reversed_walk_2 = pygame.transform.flip(player_walk_2, True, False)
player_reversed_walk_3 = pygame.transform.flip(player_walk_3, True, False)
player_reversed_walk_4 = pygame.transform.flip(player_walk_4, True, False)
player_reversed_walk_5 = pygame.transform.flip(player_walk_5, True, False)

upgrades = [{
    "name": "CHEESE",
    "cost": 100,
    "description": "CHEESE",
    "var": [bottle_collect_dist, 0],
    "amountchanged": [1000, 0],
    "texture": bottle_large_img,
    "type": [upgradetypes.INCREMENT, upgradetypes.NONE]
}, {
    "name": "Bottle collect distance",
    "cost": 1,
    "description": "Bottle collect distance +10",
    "var": [bottle_collect_dist, 0],
    "amountchanged": [10, 0],
    "texture": bottle_large_img,
    "type": [upgradetypes.INCREMENT, upgradetypes.NONE]
}, {
    "name": "Bottle distance & Speed",
    "cost": 1,
    "description": "Bottle collect distance +10 & Player speed +300",
    "var": [bottle_collect_dist, playerspeed],
    "amountchanged": [10, 300],
    "texture": bottle_large_img,
    "type": [upgradetypes.REDEFINE, upgradetypes.REDEFINE]
}, {
    "name": "Bottle distance & Speed",
    "cost": 1,
    "description": "Bottle collect distance +10 & Player speed +300",
    "var": [bottle_collect_dist, playerspeed],
    "amountchanged": [10, 300],
    "texture": bottle_large_img,
    "type": [upgradetypes.REDEFINE, upgradetypes.REDEFINE]
}]


def create_structure(space, info):
  """Creates static physical boundaries for the level."""
  body = space.static_body
  shape = pymunk.Poly.create_box(body, (info["w"], info["h"]))
  # Pymunk uses center coordinates
  shape.body.position = (info["x"] + info["w"] / 2,
                         info["y"] + info["h"] / 2)
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

def create_bottle(space, pos: pymunk.Vec2d):
  """Creates a physics-enabled bottle."""
  mass = 1
  bottle_shape = [(10, 10), (10, -10), (-10, -10), (-10, 10)]
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


def create_plate(space, pos: pymunk.Vec2d):
  mass = 1
  bottle_shape = [(10, 10), (10, -10), (-10, -10), (-10, 10)]
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


def create_soda(space, pos: pymunk.Vec2d):
  mass = 1
  bottle_shape = [(7, 10), (7, -10), (-7, -10), (-7, 10)]
  moment = pymunk.moment_for_poly(mass, bottle_shape)
  body = pymunk.Body(mass, moment)
  body.position = pos
  shape = pymunk.Poly(body, bottle_shape)
  shape.friction = 0.8
  space.add(body, shape)
  twashstruct = Struct()
  twashstruct.type = trashtypes.SODA
  twashstruct.shape = shape
  return twashstruct

def getinput(player_shape, isreversed, screen):
    """Handles movement: Left, Right, and Jump."""
    keys = pygame.key.get_pressed()
    v = player_shape.body.velocity
    player_shape.body.angle = 0
    testtext = textbox.textbox("Hello World!")
    if keys[pygame.K_LEFT]:
        player_shape.body.velocity = (-playerspeed, v.y)
        isreversed = True
    elif keys[pygame.K_RIGHT]:
        player_shape.body.velocity = (playerspeed, v.y)
        isreversed = False
    else:
        player_shape.body.velocity = (0, v.y)

    # Simple Jump (only if vertical velocity is near zero)
    if keys[pygame.K_UP] and abs(v.y) < 0.2:
        player_shape.body.velocity = (v.x, -400)
        player_shape.body.angle = 0
    elif keys[pygame.K_f]:
        print("VEL: " + str(player_shape.body.velocity) + " POS: " +
              str(player_shape.body.position) + " ANGLE: " +
              str(player_shape.body.angle))
    elif keys[pygame.K_e]:
        testtext = textbox.textbox("Hello World!")
        testtext.HEIGHT = HEIGHT
        testtext.WIDTH = WIDTH
    return isreversed, testtext

def physics(player, space, clock):
    """Updates the physics simulation."""
    num = 150
    phy = (1 / num)
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
    for b in range(20):
        bottle_x.append(random.randint(50, 100))

    for i in range(len(bottle_x)):
        type = random.randint(1, 3)
        if type == 1:
            bottles.append(create_bottle(space, (bottle_x[i], 200)))
        elif type == 2:
            bottles.append(create_plate(space, (bottle_x[i], 200)))
        elif type == 3:
            bottles.append(create_soda(space, (bottle_x[i], 200)))
    return bottles


def generateWhiteNoise(width, height):
    noise = [[r for r in range(width)] for i in range(height)]

    for i in range(0, height):
        for j in range(0, width):
            noise[i][j] = random.randint(0, 4)

    return noise


def twashthead(items, space):
    type = random.randint(1, 3)
    if type == 1:
        items.append(create_bottle(space, (random.randint(50, 780), 200)))
    elif type == 2:
        items.append(create_plate(space, (random.randint(50, 780), 200)))
    elif type == 3:
        items.append(create_soda(space, (random.randint(50, 780), 200)))

def renderer(render):
    for item in render:
        item["func"](item["args"])

def shop(shop_open, screen, WIDTH, HEIGHT, twash_coin, button_highlight, button_highlight_GEORGE, shop_open_delay, upgradearray_index, upgradearray_variable_index, bottles_collected, render):
        mouse = Mouse()
        mouse.x = pygame.mouse.get_pos()[0]
        mouse.y = pygame.mouse.get_pos()[1]

        #screen.fill((175, 175, 175))
        render.append({"func" : screen.fill((175, 175, 175)), "args" : ((175, 175, 175))})
        #pygame.draw.rect(screen, (101, 67, 33), (100, 100, 600, 400))
        render.append({"func" : pygame.draw.rect(screen, (101, 67, 33), (100, 100, 600, 400)), "args" : (screen, (101, 67, 33), (100, 100, 600, 400))})
        #pygame.draw.rect(screen, (101, 67, 33), (150, 150, 500, 300))
        render.append({"func" : pygame.draw.rect(screen, (101, 67, 33), (150, 150, 500, 300)), "args" : (screen, (101, 67, 33), (150, 150, 500, 300))})
        #pygame.draw.rect(screen, (101, 67, 33), (200, 200, 400, 200))
        render.append({"func" : pygame.draw.rect(screen, (101, 67, 33), (200, 200, 400, 200)), "args" : (screen, (101, 67, 33), (200, 200, 400, 200))})
        #pygame.draw.rect(screen, (101, 67, 33), (250, 250, 300, 100))
        render.append({"func" : pygame.draw.rect(screen, (101, 67, 33), (250, 250, 300, 100)), "args" : (screen, (101, 67, 33), (250, 250, 300, 100))})
        #pygame.draw.rect(screen, (101, 67, 33), (300, 300, 200, 50))
        render.append({"func" : pygame.draw.rect(screen, (101, 67, 33), (300, 300, 200, 50)), "args" : (screen, (101, 67, 33), (300, 300, 200, 50))})
        #screen.blit(shop_img, (100, 100))
        render.append({"func" : screen.blit(shop_img, (100, 100)), "args" : (shop_img, (100, 100))})
        font = pygame.font.Font(None, 16)
        try:
            name = font.render(upgrades[upgradearray_index]["name"], True,
                               pygame.Color("white"))
            desc = font.render(upgrades[upgradearray_index]["description"],
                               True, pygame.Color("white"))
            cost = font.render(str(upgrades[upgradearray_index]["cost"]),
                               True, pygame.Color("white"))
            name2 = font.render(upgrades[upgradearray_index + 1]["name"],
                                True, pygame.Color("white"))
            desc2 = font.render(
                upgrades[upgradearray_index + 1]["description"], True,
                pygame.Color("white"))
            cost2 = font.render(
                str(upgrades[upgradearray_index + 1]["cost"]), True,
                pygame.Color("white"))
        except:
            print("No more upgrades!")
            name = font.render("No more upgrades!", True,
                               pygame.Color("white"))
        try:
            render.append({ "func" : screen.blit(upgrades[upgradearray_index]["texture"],
                        (140, 180)), "args" : (upgrades[upgradearray_index]["texture"],
                        (140, 180))})
        except:
            print("No more upgrades!")
        #screen.blit(name, (250, 190))
        render.append({"func" : screen.blit(name, (250, 190)), "args" : (name, (250, 190))})
        #screen.blit(desc, (250, 200))
        render.append({"func" : screen.blit(desc, (250, 200)), "args" : (desc, (250, 200))})
        #screen.blit(cost, (250, 210))
        render.append({"func" : screen.blit(cost, (250, 210)), "args" : (cost, (250, 210))})
        try:
            #screen.blit(upgrades[upgradearray_index + 1]["texture"],(440, 180))
            render.append({"func" : screen.blit(upgrades[upgradearray_index + 1]["texture"],(440, 180)), "args" : (upgrades[upgradearray_index + 1]["texture"],(440, 180))})
        except:
            print("No more upgrades!")
        #screen.blit(name2, (550, 190))
        render.append({"func" : screen.blit(name2, (550, 190)), "args" : (name2, (550, 190))})
        #screen.blit(desc2, (550, 200))
        render.append({"func" : screen.blit(desc2, (550, 200)), "args" : (desc2, (550, 200))})
        #screen.blit(cost2, (550, 210))
        render.append({"func" : screen.blit(cost2, (550, 210)), "args" : (cost2, (550, 210))})

        keys = pygame.key.get_pressed()
        if pygame.mouse.get_pressed():
            if mouse.x >= 140 and mouse.x <= 390 and mouse.y <= 480 and mouse.y >= 180:
                try:
                    if twash_coin >= upgrades[upgradearray_index]["cost"]:
                        if shop_open_delay.isdelayed():
                            if upgradearray_index == len(upgrades) - 1:
                                print("No more upgrades!")
                            else:
                                print("Bought item!")
                                twash_coin = twash_coin - upgrades[
                            upgradearray_index]["cost"]
                                for upgrade_var in upgrades[upgradearray_index][
                                "var"]:
                                    if upgrades[upgradearray_index]["type"][
                                        upgradearray_variable_index] == upgradetypes.INCREMENT:
                                        upgrades[upgradearray_index]["var"][
                                    upgradearray_variable_index] = upgrades[
                                        upgradearray_index]["var"][
                                            upgradearray_variable_index] + upgrades[
                                                upgradearray_index][
                                                    "amountchanged"][
                                                        upgradearray_variable_index]
                                    elif upgrades[upgradearray_index]["type"][
                                        upgradearray_variable_index] == upgradetypes.DECREMENT:
                                        upgrades[upgradearray_index]["var"][
                                    upgradearray_variable_index] = upgrades[
                                        upgradearray_index]["var"][
                                            upgradearray_variable_index] - upgrades[
                                                upgradearray_index][
                                                    "amountchanged"][
                                                        upgradearray_variable_index]
                                    elif upgrades[upgradearray_index]["type"][
                                    upgradearray_variable_index] == upgradetypes.REDEFINE:
                                        upgrades[upgradearray_index]["var"][
                                    upgradearray_variable_index] = upgrades[
                                        upgradearray_index][
                                            "amountchanged"][
                                                upgradearray_variable_index]
                        upgradearray_index = upgradearray_index + 1
                except:
                    print("No more upgrades!")
            if mouse.x >= 420 and mouse.x <= 690 and mouse.y <= 480 and mouse.y >= 180:
                try:
                    if twash_coin >= upgrades[upgradearray_index +
                                              1]["cost"]:

                        if upgradearray_index == len(upgrades) - 2:
                            print("No more upgrades!")
                        else:
                            print("Bought item!")
                            twash_coin = twash_coin - upgrades[
                                upgradearray_index + 1]["cost"]
                            for upgrade_var in upgrades[upgradearray_index
                                                        + 1]["var"]:
                                if upgrades[upgradearray_index + 1][
                                        "type"] == upgradetypes.INCREMENT:
                                    upgrades[upgradearray_index +
                                             1]["var"] = upgrades[
                                                 upgradearray_index +
                                                 1]["var"] + upgrades[
                                                     upgradearray_index +
                                                     1]["amountchanged"]
                                elif upgrades[upgradearray_index + 1][
                                        "type"] == upgradetypes.DECREMENT:
                                    upgrades[upgradearray_index +
                                             1]["var"] = upgrades[
                                                 upgradearray_index +
                                                 1]["var"] - upgrades[
                                                     upgradearray_index +
                                                     1]["amountchanged"]
                                elif upgrades[upgradearray_index + 1][
                                        "type"] == upgradetypes.REDEFINE:
                                    upgrades[upgradearray_index +
                                             1]["var"] = upgrades[
                                                 upgradearray_index +
                                                 1]["amountchanged"]
                            upgradearray_index = upgradearray_index + 1
                except:
                    print("No more upgrades!")
        if mouse.x >= 140 and mouse.x <= 390 and mouse.y <= 480 and mouse.y >= 180:
            #screen.blit(button_highlight, (140, 180))
            render.append({"func" : screen.blit(button_highlight, (140, 180)), "args" : (button_highlight, (140, 180))})
        if mouse.x >= 420 and mouse.x <= 690 and mouse.y <= 480 and mouse.y >= 180:
            #screen.blit(button_highlight_GEORGE, (420, 180))
            render.append({"func" : screen.blit(button_highlight_GEORGE, (420, 180)), "args" : (button_highlight_GEORGE, (420, 180))})

        if bottles_collected >= 100 and keys[pygame.K_q]:
            twash_coin = twash_coin + 1
            bottles_collected = bottles_collected - 100


def main(playerdirection, WIDTH, HEIGHT):

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Landfill Cleaner - Apps for Good")
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    bottles_collected = 0
    twash_coin = 100
    shop_open = False
    currentfps = clock.get_fps()
    button_highlight = pygame.Surface((250, 300))
    button_highlight.fill((255, 0, 0))
    button_highlight.set_alpha(128)
    button_highlight_GEORGE = pygame.Surface((240, 300))
    button_highlight_GEORGE.fill((255, 0, 0))
    button_highlight_GEORGE.set_alpha(128)
    

    player_walk_animation = animation.Animation([player_walk_1, player_walk_2, player_walk_3, player_walk_4, player_walk_5, player_walk_4, player_walk_3, player_walk_2], int((currentfps*100)))
    player_walk_animation_reversed = animation.Animation([player_reversed_walk_1, player_reversed_walk_2, player_reversed_walk_3, player_reversed_walk_4, player_reversed_walk_5, player_reversed_walk_4, player_reversed_walk_3, player_reversed_walk_2], int((currentfps*100)))

    # Rendering thread setup
    render = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    executor.submit(renderer, render)
    
    get_account("","")

    # Physics Space
    space = pymunk.Space()
    space.gravity = (0, 950)  # Gravity pulls down

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
    upgradearray_index = 0
    upgradearray_variable_index = 0

    running = True
    while running:
        current_time = pygame.time.get_ticks() / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        render = []
        shop_open_delay = delay.Delay((currentfps*0.6))
        currentfps = clock.get_fps()
        # bottle spawning everyb 2 sec code:
        WIDTH, HEIGHT = pygame.display.get_surface().get_size(
        )[0], pygame.display.get_surface().get_size()[1]

        # 1. Input
        playerdirection, testtext = getinput(player, playerdirection, screen)

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

        shop_open_delay.total_delay = (currentfps*0.6)
        if shop_open_delay.isdelayed():
            if keys[pygame.K_f]:
                if shop_open:
                    shop_open = False
                else:
                    shop_open = True
        else:
            shop_open_delay.tick()

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
        camera_offset = Vec2d(WIDTH / 2 - player.body.position.x,
                              HEIGHT / 2 - player.body.position.y)

        if not shop_open:

            render.append({"func" : screen.fill((199, 169, 84)) ,"args": (199, 169, 84)})  # Not So Sky Blue Blue

            # Draw Platforms
            for item in zoo_level:
                render.append({"func" :pygame.draw.rect(screen, (82, 82, 82),
                                 (item["x"] + camera_offset.x, item["y"] +
                                  camera_offset.y, item["w"], item["h"])) , "args" : (screen, (82, 82, 82),
                               (item["x"] + camera_offset.x, item["y"] +
                                camera_offset.y, item["w"], item["h"]))})
            player_walk_animation.delay.total_delay = int(currentfps)
            player_walk_animation_reversed.delay.total_delay = int(currentfps)
            if playerdirection:
                if not player.body.velocity.x <= -0.4:
                    render.append({"func" : screen.blit(player_reversed_img,
                            (player.body.position - Vec2d(17, 10)) +
                            camera_offset), "args" : (player_reversed_img,
                            (player.body.position - Vec2d(17, 10)) +
                            camera_offset) })
                else:
                    player_walk_animation_reversed.dotick()
                    render.append({"func" : screen.blit(player_walk_animation_reversed.getframe(), (player.body.position - Vec2d(17, 10)) +
                                camera_offset), "args" : (player_walk_animation_reversed.getframe(), (player.body.position - Vec2d(17, 10)) +
                                camera_offset)})
            else:
                if player.body.velocity.x <= 0.4:
                    render.append({"func" : screen.blit(player_img,
                            (player.body.position - Vec2d(17, 10)) +
                        camera_offset), "args" : (player_img,
                            (player.body.position - Vec2d(17, 10)) +
                            camera_offset)})
                else:
                    player_walk_animation.dotick()
                    render.append({"func" : screen.blit(player_walk_animation.getframe(), (player.body.position - Vec2d(17, 10)) + camera_offset), "args" : (player_walk_animation.getframe(), (player.body.position - Vec2d(17, 10)) + camera_offset)})
            
                                   
                                   
                    #  screen.blit(bottle_large_img, player.body.position-Vec2d(60,110)+camera_offset)

            for item in items:
                if item.shape.body.position.y > HEIGHT:
                    space.remove(item.shape.body, item.shape)
                    items.remove(item)
                elif item.shape.body.position.x <= player.body.position.x + bottle_collect_dist and item.shape.body.position.x >= player.body.position.x - bottle_collect_dist and item.shape.body.position.y <= player.body.position.y + bottle_collect_dist and item.shape.body.position.y >= player.body.position.y - bottle_collect_dist:
                    space.remove(item.shape.body, item.shape)
                    items.remove(item)
                    if item.type == trashtypes.BOTTLE:
                        print("Bottle collected!")
                        bottles_collected = bottles_collected + 1
                    elif item.type == trashtypes.RUSTYMETAL:
                        print("Rusty metal collected!")
                        bottles_collected = bottles_collected + 2
                    elif item.type == trashtypes.SODA:
                        print("Soda collected!")
                        bottles_collected = bottles_collected + 3
                else:
                    item.shape.body.angle = 0
                    item.shape.body.velocity = (0, item.shape.body.velocity.y)
                    if item.type == trashtypes.BOTTLE:
                        render.append({"func" : screen.blit(
                            bottle_img,
                            (item.shape.body.position - Vec2d(17, 20)) +
                            camera_offset), "args" : (bottle_img,
                            (item.shape.body.position - Vec2d(17, 20)) +
                            camera_offset)})
                    elif item.type == trashtypes.RUSTYMETAL:
                        render.append({"func" : screen.blit(
                            rustymetal_img,
                            (item.shape.body.position - Vec2d(17, 20)) +
                            camera_offset), "args" : (rustymetal_img,
                            (item.shape.body.position - Vec2d(17, 20)) +
                            camera_offset)})
                    elif item.type == trashtypes.SODA:
                        render.append({"func" : screen.blit(
                            soda_img,
                            (item.shape.body.position - Vec2d(17, 20)) +
                            camera_offset), "args" : (soda_img,
                            (item.shape.body.position - Vec2d(17, 20)) +
                            camera_offset)})

            # Draw Player (using pymunk helper for simplicity)
            if debug:
                render.append({"func" : space.debug_draw(draw_options), "args" : (draw_options)})
            if keys[pygame.K_e]:
                render.append({"func" : testtext.draw(screen), "args" : (screen)})

        elif shop_open:
           shop(shop_open, screen, WIDTH, HEIGHT, twash_coin, button_highlight, button_highlight_GEORGE, shop_open_delay, upgradearray_index, upgradearray_variable_index, bottles_collected, render)

        # Display fps
        mouse = Mouse()
        mouse.x = pygame.mouse.get_pos()[0]
        mouse.y = pygame.mouse.get_pos()[1]
        uptime = "Uptime: " + str(int(pygame.time.get_ticks() / 1000))
        fps = "FPS: " + str(int(clock.get_fps()))  # ok
        bottles_gotten = "Rubbish Collected: " + str(bottles_collected)
        Twash_coin = "Twash Coin: " + str(twash_coin)
        mouse_coords = "Mouse: " + str(mouse.x) + ", " + str(mouse.y)
        y = 5
        font = pygame.font.Font(None, 16)
        bottle_text = font.render(bottles_gotten, True, pygame.Color("black"))
        text = font.render(fps, True, pygame.Color("black"))
        coin_text = font.render(Twash_coin, True, pygame.Color("black"))
        mouses_coods = font.render(mouse_coords, True, pygame.Color("black"))
        uptime_text = font.render(uptime, True, pygame.Color("black"))
        render.append({"func" : screen.blit(text, (5, y)), "args" : (text, (5, y))})
        #screen.blit(text, (5, y))
        render.append({"func" : screen.blit(bottle_text, (5, y + 10)), "args" : (bottle_text, (5, y + 10))})
        #screen.blit(bottle_text, (5, y + 10))
        render.append({"func" : screen.blit(coin_text, (5, y + 20)), "args" : (coin_text, (5, y + 20))})
        #screen.blit(coin_text, (5, y + 20))
        render.append({"func" : screen.blit(mouses_coods, (5, y + 30)), "args" : (mouses_coods, (5, y + 30))})
        #screen.blit(mouses_coods, (5, y + 30))
        render.append({"func" : screen.blit(uptime_text, (5, y + 40)), "args" : (uptime_text, (5, y + 40))})
        #screen.blit(uptime_text, (5, y + 40))

        pygame.display.flip()
        clock.tick(FPS)
        fps = str(clock.get_fps())
<<<<<<< HEAD
=======

    pygame.quit()
>>>>>>> ea6627fc545abc6dfb63a7874e581232b58b28ae
    executor.shutdown(wait=True)

if __name__ == "__main__":
    # executor = ThreadPoolExecutor(max_workers=1)
    # executor.submit(main, playerdirection)
    # executor.shutdown(wait=True)
    # print("Done!")
    #      p = mp.Process(target=main, args=(playerdirection,))
    main(playerdirection, WIDTH, HEIGHT)
    #      p.start()
<<<<<<< HEAD
    #      p.join()
=======
    #      p.join()

>>>>>>> ea6627fc545abc6dfb63a7874e581232b58b28ae
