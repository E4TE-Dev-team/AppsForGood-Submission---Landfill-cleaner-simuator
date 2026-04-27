import pygame

class textbox:
  textsize = 16
  textcolor = pygame.Color("black")
  padding = 1
  y = 0
  x = 0
  WIDTH = 800
  HEIGHT = 600
  def __init__(self, text) -> None:
      self.text = text
      self.font = pygame.font.Font(None, self.textsize)
      self.textsurface = self.font.render(self.text, True, self.textcolor)
      self.y = (self.HEIGHT / 2) - self.textsurface.get_height() - self.padding
      self.x = (self.WIDTH / 2) - self.textsurface.get_width() - self.padding

  def draw(self, screen):
      pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.textsurface.get_width() + self.padding, self.textsurface.get_height() + self.padding))
      screen.blit(self.textsurface, (self.x + self.padding, self.y + self.padding))
      self.y = (self.HEIGHT / 2) - self.textsurface.get_height() - self.padding
      self.x = (self.WIDTH / 2) - self.textsurface.get_width() - self.padding