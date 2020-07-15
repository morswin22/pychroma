from pychroma import Sketch

class Numpad(Sketch):
  colors = [
    (221, 221, 221),
    (30, 255, 0),
    (0, 112, 221),
    (163, 53, 238),
    (255, 128, 0)
  ]

  @property
  def value(self):
    return self.__value

  @value.setter
  def value(self, new):
    self.__value = new
    self.render()

  def render(self):
    digits = [digit for digit in str(self.value)]
    for i in range(10):
      self.keyboard.set_grid(self.controller.keys_info['positions'][f"num_{i}"], (0,0,0))
    for i, j in enumerate(reversed(digits)):
      self.keyboard.set_grid(self.controller.keys_info['positions']["num_"+j], self.colors[i])
