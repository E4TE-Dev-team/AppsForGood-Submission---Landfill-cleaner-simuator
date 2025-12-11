__docformat__ = "reStructuredText"
import sys
import os
import subprocess

import pygame

import pymunk
import pymunk.pygame_util
from pymunk import Vec2d


def main():

    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()
    running = True

    ### Physics stuff
    space = pymunk.Space()
    space.gravity = Vec2d(0.0, -900.0)
    
    
