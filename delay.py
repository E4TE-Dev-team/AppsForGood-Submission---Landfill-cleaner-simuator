import pygame


class Delay:
    current_delay = 0
    total_delay = 0
    delayed = False

    def __init__(self, delay):
        self.total_delay = delay

    def tick(self):
        if self.current_delay >= self.total_delay:
            self.delayed = True
            self.current_delay = 0
        else:
            self.current_delay += 1

    def isdelayed(self):
        if self.delayed:
            self.delayed = False
            return True
        else:
            return False
