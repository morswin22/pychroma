import json
import threading
import time
import os

from pynput import keyboard

from .Autocomplete import Autocomplete
from .Connection import Connection
from .Device import Device


class ControllerError(Exception):
  pass

def parse_key(key):
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

class Controller:
  defined = False

  def __init__(self, config_path):
    Controller.defined = True
    self.config(config_path)
    self.create_connection()
    self.bind_listeners()
    self.reset_events_listeners()
    self.reset_sketch()

  def __del__(self):
    self.stop()

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.stop()

  def stop(self):
    self.reset_sketch()
    self.connection.stop()

  def config(self, path):
    with open(path, 'r') as file:
      self.configuration = json.load(file)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'map.json'), 'r') as file:
      self.device_mapping = json.load(file)

  def create_connection(self):
    if 'chroma' in self.configuration:
      self.connection = Connection(self.configuration['chroma'])
    else:
      raise ControllerError('Not found Chroma SDK credentials in configuration file')

  def connect(self):
    if not self.connection.is_connected():
      self.connection.connect()
      self.devices = []
      for name in self.configuration['chroma']['supportedDevices']:
        if 'devices' in self.configuration and name in self.configuration['devices']:
          device_name = self.configuration['devices'][name]
          if device_name in self.device_mapping[name]['devices']:
            layout_id = self.device_mapping[name]['devices'][device_name]
            device = Device(self.connection.url, name, self.device_mapping[name]['layouts'][layout_id])
          else:
            print(f'pychroma INFO: Layout for {device_name} is not available, consider adding it in a pull request')
            device = Device(self.connection.url, name)
        else:
          device = Device(self.connection.url, name)
        self.devices.append(device)
      time.sleep(1.5)

  def disconnect(self):
    self.devices = []
    if self.connection.is_connected():
      self.connection.disconnect()

  def get_device(self, name):
    for device in self.devices:
      if device.name == name:
        return device
    raise ControllerError(f'Not found device with this name "{name}"')

  def bind_listeners(self):
    self.keys = {}
    self.keyboard_listener = keyboard.Listener(
      on_press=self.on_key_press, 
      on_release=self.on_key_release
    )
    self.keyboard_listener.start()

  def on_key_press(self, key):
    self.keys[key] = True
    if self.sketch:
      self.sketch.on_key_press(key)

  def on_key_release(self, key):
    self.keys[key] = False
    if self.sketch:
      self.sketch.on_key_release(key)

  def is_pressed(self, key):
    return key in self.keys

  def reset_events_listeners(self):
    self.events_listeners = {}
    self.last_event_listener_id = 0

  def subscribe(self, event_name, callback, time_to_live=-1):
    if not event_name in self.events_listeners:
      self.events_listeners[event_name] = []
    self.events_listeners[event_name].append((self.last_event_listener_id, callback, time_to_live))
    self.last_event_listener_id += 1

  def unsubscribe(self, event_name, listener_id):
    if event_name in self.events_listeners:
      delete_index = None
      for index, (current_id, callback, time_to_live) in enumerate(self.events_listeners[event_name]):
        if listener_id == current_id:
          delete_index = index
          break
      if delete_index is not None:
        self.events_listeners[event_name].pop(delete_index)

  def emit(self, event_name, *argv):
    if event_name in self.events_listeners:
      for index, (listener_id, callback, time_to_live) in enumerate(self.events_listeners[event_name]):
        if time_to_live == 0:
          self.unsubscribe(event_name, listener_id)
        else:
          if time_to_live > 0:
            time_to_live -= 1
            self.events_listeners[event_name][index] = (listener_id, callback, time_to_live)
          callback(*argv)

  def reset_sketch(self):
    if 'sketch' in self.__dict__ and self.sketch is not None:
      self.sketch.stop()
    self.sketch = None

  def run_sketch(self, Sketch):
    self.connect()

    self.sketch = Sketch()
    self.sketch.setup_with_controller(self)

    while self.sketch.alive:
      self.sketch.update()
      self.sketch.render()

      for device in self.devices:
        device.render()

      time.sleep(self.sketch.interval)

  def reset_commands(self):
    self.commands = None

  def use_commands(self):
    self.commands = {}
    self.stored_sketch = None

  def add_command(self, command, callback):
    if self.commands is not None:
      if not command in self.commands:
        self.commands[command] = callback
      else:
        raise ControllerError(f'Command {command} is already set')
    else:
      raise ControllerError('Enable commands using use_commands method')

  def add_commands(self, commands):
    if self.commands is not None:
      if isinstance(commands, dict):
        self.commands = commands
      else:
        raise ControllerError('Passed commands should be in dictionary')
    else:
      raise ControllerError('Enable commands using use_commands method')
