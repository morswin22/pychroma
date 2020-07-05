from pychroma import Sketch

class Numpad(Sketch):
  colors = [
    '#dddddd',
    '#1eff00',
    '#0070dd',
    '#a335ee',
    '#ff8000'
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
