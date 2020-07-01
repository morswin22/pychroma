from Sketch import Sketch

class Dot:
  id = 0
  def __init__(self, pos, color):
    self.step = 0
    self.pos = [pos[0], pos[1]]
    self.color = color
    self.id = Dot.id
    Dot.id += 1

class Hello(Sketch):
  def setup(self):
    self.frame_rate = 1/18
    self.starting_position = (10, 5)
    self.dots = []
    self.dots_data = [
      (0, 0, 0),
      (0, 0, 255),
      (0, 127, 127),
      (0, 255, 0),
      (127, 127, 0),
      (255, 0, 0)
    ] + [
      (127, 0, 127),
      (0, 0, 255),
      (0, 127, 127),
      (0, 255, 0),
      (127, 127, 0),
      (255, 0, 0)
    ] * 3

  def update(self):
    if len(self.dots_data) > 0:
      self.dots.append(Dot(self.starting_position, self.dots_data.pop()))

    for dot in self.dots:
      if dot.step == 0:
        dot.step = 1
      elif dot.step == 1:
        dot.pos[0] -= 1
        if dot.pos[0] == 0:
          dot.step = 2
      elif dot.step == 2:
        dot.pos[1] -= 1
        if dot.pos[1] == 0:
          dot.step = 3
      elif dot.step == 3:
        dot.pos[0] += 1
        if dot.pos[0] == 11:
          dot.step = 4
          if dot.id == len(self.dots) - 1:
            self.controller.soft(self.controller.idle)

  def fix(self, x, y):
    if y == 5 and 4 <= x <= 8:
      x = 7
    elif x == 0 and 0 <= y <= 5:
      x = 1
    elif x == 18 and y == 5:
      x = 19
    elif  18 <= x <= 21 and y == 0:
      x = 17
    elif x == 21:
      if y == 5:
        y = 4
      elif y == 3:
        y = 2
    elif x == 2 and y == 0:
      x = 3
    return x, y

  def render(self):
    for dot in reversed(self.dots):
      if dot.step != 4:
        for (x, y) in (self.fix(dot.pos[0], dot.pos[1]), self.fix(21 - dot.pos[0], dot.pos[1])):
          self.keyboard.grid[y][x].set(red=dot.color[0], green=dot.color[1], blue=dot.color[2])
