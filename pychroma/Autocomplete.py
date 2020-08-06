from .Sketch import Sketch


class Autocomplete(Sketch):
  connect = False

  def setup(self):
    self.dump_buffer()
    self.connected = False

  def connect(self):
    self.controller.connect()
    self.setup_devices(self.controller.devices) # TODO recover devices color_mode
    self.connected = True

  def disconnect(self):
    if self.controller.sketch is None:
      self.controller.disconnect()
    self.connected = False

  def dump_buffer(self):
    self.write_buffer = []

  def on_key_press(self, key):
    if key == self.accept_key:
      command = "".join(self.write_buffer)
      if command in self.controller.commands:
        self.dump_buffer()
        self.controller.commands[command]()
        if self.controller.sketch is None:
          self.disconnect()
    elif key == self.delete_key:
      if len(self.write_buffer):
        self.write_buffer.pop()
    elif len(key) == 1:
      self.write_buffer.append(key)

    self.render()

  def render(self):
    if not self.connected:
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

    self.keyboard.render()
