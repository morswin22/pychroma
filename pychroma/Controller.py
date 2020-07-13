import json
import threading
import time

from pynput import keyboard

from .Autocomplete import Autocomplete
from .Connection import Connection
from .Device import Device


class ControllerError(Exception):
  pass

class Controller(threading.Thread):
  def __init__(self, config_path):
    threading.Thread.__init__(self)

    self.commands = {}
    self.devices = []
    self.keys = {}
    self.sketch = None
    self.stored_sketch = None
    self.soft_list = []
    self.paused = False
    self.pause_cond = threading.Condition(threading.Lock())
    self.connection = None
    self.alive = True

    self.config(config_path)
    self.bind_listeners()
    self.pause()

  def config(self, path):
    with open(path, 'r') as file:
      data = json.load(file)
      self.connection_info = data['chroma']
      self.keys_info = data['keys']
      self.misc_info = data['misc']

  def connect(self):
    if self.connection is None:
      self.connection = Connection(self.connection_info)
      self.devices = []
      for name in self.connection_info['supportedDevices']:
        self.devices.append(Device(self.connection.url, name))
      time.sleep(1.5)

  def disconnect(self):
    if self.connection is not None:
      self.connection.stop()
    self.connection = None
    self.devices = []

  def bind_listeners(self):
    self.listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
    self.listener.start()

  def render(self):
    for device in self.devices:
      device.render()

  def find(self, predicate):
    for device in self.devices:
      if predicate(device):
        return device

  @property
  def keyboard(self):
    return self.find(lambda device: device.name == "keyboard")

  @property
  def mouse(self):
    return self.find(lambda device: device.name == "mouse")

  @property
  def mousepad(self):
    return self.find(lambda device: device.name == "mousepad")

  @property
  def keypad(self):
    return self.find(lambda device: device.name == "keypad")

  @property
  def headset(self):
    return self.find(lambda device: device.name == "headset")

  @property
  def chromalink(self):
    return self.find(lambda device: device.name == "chromalink")

  def on_key_press(self, key):
    if self.parse_key(key) == self.keys_info['pause']:
      if isinstance(self.sketch, Autocomplete):
        self.restore_sketch()
      else:
        self.soft(lambda: self.run_sketch(Autocomplete))
        self.store_sketch()
    else:
      self.keys[key] = True
      if self.sketch:
        self.sketch.on_key_press(key)

  def on_key_release(self, key):
    self.keys[key] = False
    if self.sketch:
      self.sketch.on_key_release(key)

  def is_pressed(self, key):
    return key in self.keys

  def parse_key(self, key):
    if 'char' in key.__dict__:
      if key.char != None:
        return key.char
      elif 'vk' in key.__dict__:
        if 96 <= key.vk <= 105:
          return f"num_{key.vk - 96}"
        else:
          return f"<{key.vk}>"
    elif '_name_' in key.__dict__:
      return key._name_

  def add_command(self, name, callback):
    self.commands[name] = callback

  def do_run(self, Sketch):
    return lambda: self.soft(lambda: self.run_sketch(Sketch))

  def run_sketch(self, Sketch):
    self.connect()
    self.soft_list = []

    self.sketch = Sketch(self)
    self.sketch.setup()

    self.resume()

  def run(self):
    while self.alive:
      with self.pause_cond:
        while self.paused:
          self.pause_cond.wait()

        if self.sketch is not None:
          self.sketch.update()
          self.sketch.render()
          self.render()
          if self.sketch.frame_rate:
            time.sleep(self.sketch.frame_rate)

          for callback in self.soft_list:
            callback()
          self.soft_list = []

  def soft(self, callback):
    if self.paused:
      callback()
    else:
      self.soft_list.append(callback)

  def pause(self):
    if not self.paused:
      self.paused = True
      self.pause_cond.acquire()

  def resume(self):
    if self.paused and self.sketch.frame_rate != None:
      self.paused = False
      self.pause_cond.notify()
      self.pause_cond.release()

  def store_sketch(self):
    if self.sketch is not None and not isinstance(self.sketch, Autocomplete):
      self.stored_sketch = self.sketch
    self.soft(self.pause)

  def restore_sketch(self):
    self.sketch = self.stored_sketch
    self.stored_sketch = None
    if self.sketch is not None:
      self.connect()
      if not self.sketch.frame_rate:
        pass # Should notify the sketch about resuming
      self.resume()
    else:
      self.idle()

  def idle(self):
    self.disconnect()
    self.sketch = None
    self.stored_sketch = None
    self.pause()

  def quit(self):
    self.disconnect()
    self.alive = False
    if self.paused:
      self.paused = False
      self.pause_cond.notify()
      self.pause_cond.release()

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, type, value, traceback):
    self.join()
