import delay

class Animation:
  def __init__(self, frames, delaya):
     self.frames = frames
     self.delay = delay.Delay(delaya)
     self.current_frame = 0

  def dotick(self):
     self.delay.tick()
     if self.delay.isdelayed():
        self.current_frame += 1
        if self.current_frame >= len(self.frames):
           self.current_frame = 0
           return self.frames[self.current_frame]
  def getframe(self):
      return self.frames[self.current_frame]