import time
import json

from pynput import keyboard

from ChromaPython import ChromaApp, ChromaAppInfo, ChromaGrid

class Device:
  def __init__(self, app, name):
    self.name = name
    self.grid = ChromaGrid(name)
    self.dev = getattr(app, name)

  def __str__(self):
    return f"{self.__class__}: {self.__dict__}"

class Controller:
  def __init__(self, config_path):
    self.devices = []
    self.keys = {}
    self.sketch = None
    self.frame_rate = None

    self.config(config_path)
    self.connect()
    self.load_devices(self.info.SupportedDevices)
    self.bind_listeners()

  def config(self, path):
    self.info = ChromaAppInfo()
    with open(path, 'r') as file:
      data = json.load(file)
      for key in data:
        self.info.__dict__[key] = data[key]

  def connect(self):
    self.app = ChromaApp(self.info)
    time.sleep(1)

  def load_devices(self, devices):
    for name in devices:
      self.devices.append(Device(self.app, name.capitalize()))

  def bind_listeners(self):
    self.listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
    self.listener.start()

  def draw(self):
    for i in self.devices:
      i.dev.setCustomGrid(i.grid)
      i.dev.applyGrid()

  def find(self, predicate):
    for device in self.devices:
      if predicate(device):
        return device

  @property
  def keyboard(self):
    return self.find(lambda device: device.name == "Keyboard")

  @property
  def mouse(self):
    return self.find(lambda device: device.name == "Mouse")

  @property
  def mousepad(self):
    return self.find(lambda device: device.name == "Mousepad")

  def on_key_press(self, key):
    if key == keyboard.Key.esc:
      self.sketch = None
      return False
    else:
      self.keys[key] = True
    if self.sketch:
      self.sketch.on_key_press(key)

  def on_key_release(self, key):
    self.keys[key] = False
    if self.sketch:
      self.sketch.on_key_release(key)

  def is_pressed(self, key):
    return self.keys[key] if key in self.keys else False

  def run(self, Sketch):
    self.sketch = Sketch(self)
    self.sketch.setup()

    if self.frame_rate:
      while self.sketch:
        self.sketch.update()
        self.sketch.render()
        self.draw()
        time.sleep(self.frame_rate)
