import json
import threading
import time

import pyaudio
from pynput import keyboard

from ChromaPython import ChromaApp, ChromaAppInfo, ChromaGrid
from Autocomplete import Autocomplete

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
    self.stored_sketch = None
    self.soft_list = []
    self.paused = False
    self.pause_cond = threading.Condition(threading.Lock())
    self.app = None
    self.alive = True

    self.config(config_path)
    self.bind_listeners()
    self.pause()

  def config(self, path):
    with open(path, 'r') as file:
      self.info = ChromaAppInfo()
      data = json.load(file)
      for key in data['chroma']:
        self.info.__dict__[key] = data['chroma'][key]
      self.audio_info = data['audio']
      self.keys_info = data['keys']

  def connect(self):
    if not self.app:
      self.app = ChromaApp(self.info)
      self.devices = []
      for name in self.info.SupportedDevices:
        self.devices.append(Device(self.app, name.capitalize()))
      time.sleep(1.5)

  def disconnect(self):
    self.app = None
    self.devices = []

  def bind_listeners(self):
    self.listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
    self.listener.start()
    self.audio = pyaudio.PyAudio()

  def get_audio_mix(self):
    for i in range(self.audio.get_device_count()):
      device = self.audio.get_device_info_by_index(i)
      if device['name'] == self.audio_info['name'] and device['hostApi'] == self.audio_info['hostApi']:
        return device
    return None

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
    return self.keys[key] if key in self.keys else False

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

        self.sketch.update()
        self.sketch.render()
        self.draw()
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
    if self.sketch != None and not isinstance(self.sketch, Autocomplete):
      self.stored_sketch = self.sketch
    self.soft(self.pause)

  def restore_sketch(self):
    self.sketch = self.stored_sketch
    self.stored_sketch = None
    if self.sketch != None:
      self.connect()
      if not self.sketch.frame_rate:
        print('Resuming sketch that doesn\'t have frame rate')
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