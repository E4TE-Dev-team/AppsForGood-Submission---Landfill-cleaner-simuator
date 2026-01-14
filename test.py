__docformat__ = "reStructuredText"
import sys
import os
import subprocess

import pygame

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d

zoo_level = [
    {"x" : 0 ,"y" : 0 ,"r" : 0,"type" : "block","texture" : "test"},
    {"x" : -1,"y" : 0,"r" : 180,"type" : "slope","texture" : "test"}
    ]


def getinput(space):
    
    return 0

def update(space):
    
    return 0

def draw(space):
    for i in zoo_level:
        block = i
        if block["type"] == "block":
            #render code here
            pass
        elif block["type"] == "slope":
            #render code here
            pass
        return 0


def main():

    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()
    running = True

    ### Physics stuff
    space = pymunk.Space()
    space.gravity = Vec2d(0.0, -900.0)
    
    #level geometry pymunk.Body
    world = pymunk.Body()
    world.__init__(0,0, pymunk.Body.STATIC)
    space.add(world)



    while running == True:
        getinput(space)
        update(space)
        draw(space)



main()