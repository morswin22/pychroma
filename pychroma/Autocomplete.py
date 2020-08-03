from .Sketch import Sketch


class Autocomplete(Sketch):
  connect = False

  @property
  def active(self):
    return self.activated
  
  @active.setter
  def active(self, value):
    if value is True:
      self.controller.connect()
      self.setup_devices(self.controller.devices)
    else:
      print('pychroma INFO: Disconnected from API due to Autocomplete') # TODO fix this behavior
      self.controller.disconnect()
    self.activated = value

  def setup(self):
    self.active = False
    self.write_buffer = []

  def on_key_press(self, key):
    if key == self.accept_key:
      command = "".join(self.write_buffer)
      if command in self.controller.commands:
        self.controller.commands[command]()
    elif key == self.delete_key:
      if len(self.write_buffer):
        self.write_buffer.pop()
    elif len(key) == 1: # TODO add proper check for being a char
      self.write_buffer.append(key)

    self.render()

  def render(self):
    if not self.active:
      return
    keys = []
    correct = False
    word = "".join(self.write_buffer)
    for command in self.controller.commands:
      if word == command:
        correct = True
        continue
      ok = True
      chars = [char for char in command]
      if len(chars) > len(self.write_buffer):
        for index, char in enumerate(self.write_buffer):
          if chars[index] != char:
            ok = False
            break
        if ok:
          keys.append(chars[len(self.write_buffer)])

    self.keyboard.clear()

    if correct:
      self.keyboard.set_mapped(self.accept_key, (0, 255, 0))
    
    for key in keys:
      self.keyboard.set_mapped(key, (255, 0, 0))
