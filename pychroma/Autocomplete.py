from pynput import keyboard

from .Sketch import Sketch


class Autocomplete(Sketch):
  def setup(self):
    self.write_buffer = []
    if self.controller.stored_sketch and 'commands' in self.controller.stored_sketch.__dict__:
      self.commands = self.controller.stored_sketch.commands
    else:
      self.commands = self.controller.commands
      
    self.render()

  def on_key_press(self, key):
    key_value = parse_key(key)
    if key_value == self.controller.configuration['keys']['enter']:
      command = "".join(self.write_buffer)
      if command in self.commands:
        self.commands[command]()
    elif key_value == self.controller.configuration['keys']['delete']:
      if len(self.write_buffer):
        self.write_buffer.pop()
    else:
      if 'char' in key.__dict__:
        self.write_buffer.append(key.char)

    self.render()

  def render(self):
    keys = []
    correct = False
    word = "".join(self.write_buffer)
    for command in self.commands:
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
      self.keyboard.set_grid(self.controller.configuration['keys']['positions'][self.controller.configuration['keys']['enter']], (0, 255, 0))
    
    for key in keys:
      if key in self.controller.configuration['keys']['positions']:
        self.keyboard.set_grid(self.controller.configuration['keys']['positions'][key], (255, 0, 0))

# This import needs to be here in order to prevent a circular import
from .Controller import parse_key