import json
import threading
import time

import pyaudio
from pynput import keyboard

from ChromaPython import ChromaApp, ChromaAppInfo, ChromaGrid

class Device:
  def __init__(self, app, name):
    self.name = name
    self.grid = ChromaGrid(name)
    self.dev = getattr(app, name)

  def __str__(self):
    return f"{self.__class__}: {self.__dict__}"

class Controller(threading.Thread):
  def __init__(self, config_path):
    threading.Thread.__init__(self)

    self.commands = {}
    self.devices = []
    self.keys = {}
    self.sketch = None
    self.frame_rate = None
    self.paused = False
    self.pause_cond = threading.Condition(threading.Lock())
    self.write_buffer = []
    self.writable = False
    self.app = None
    self.alive = True

    self.config(config_path)
    self.bind_listeners()
    self.pause()

  def config(self, path):
    self.info = ChromaAppInfo()
    with open(path, 'r') as file:
      data = json.load(file)
      for key in data:
        self.info.__dict__[key] = data[key]

  def connect(self):
    self.app = ChromaApp(self.info)
    self.devices = []
    for name in self.info.SupportedDevices:
      self.devices.append(Device(self.app, name.capitalize()))
    time.sleep(1)

  def disconnect(self):
    self.app = None
    self.devices = []

  def bind_listeners(self):
    self.listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
    self.listener.start()
    self.audio = pyaudio.PyAudio()

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
    if self.writable:
      if key == keyboard.Key.enter:
        command = "".join(self.write_buffer)
        print(command)
        if command in self.commands:
          self.commands[command]()
        self.writable = False
        self.write_buffer = []
      else:
        try:
          self.write_buffer.append(key.char)
        except:
          pass
    elif key == keyboard.Key.pause:
      self.writable = True
      self.pause()
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

  def add_command(self, name, callback):
    self.commands[name] = callback

  def do_run(self, Sketch):
    return lambda: self.run_sketch(Sketch)

  def run_sketch(self, Sketch):
    self.connect()

    self.sketch = Sketch(self)
    self.sketch.setup()

    if self.frame_rate:
      self.resume()

  def run(self):
    while self.alive:
      with self.pause_cond:
        while self.paused:
          self.pause_cond.wait()
        
        self.sketch.update()
        self.sketch.render()
        self.draw()
        time.sleep(self.frame_rate)

  def pause(self):
    if not self.paused:
      self.paused = True
      self.pause_cond.acquire()

  def resume(self):
    if self.paused:
      self.paused = False
      self.pause_cond.notify()
      self.pause_cond.release()

  def quit(self):
    self.disconnect()
    self.resume()
    self.alive = False

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, type, value, traceback):
    self.join()