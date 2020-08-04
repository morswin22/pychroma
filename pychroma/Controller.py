import json
import threading
import time
import os

from pynput import keyboard, mouse

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
    self.reset_events_listeners()
    self.reset_commands()
    self.bind_listeners()
    self.reset_sketch()

  def __del__(self):
    self.stop()

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self.loop()
    self.stop()

  def stop(self):
    self.alive = False
    self.reset_sketch()
    self.connection.stop()

  def config(self, path):
    with open(path, 'r') as file:
      self.configuration = json.load(file)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'map.json'), 'r') as file:
      self.device_mapping = json.load(file)

  def create_connection(self):
    self.alive = True
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
    self.buttons = {}
    self.mouse_listener = mouse.Listener(
      on_click=self.on_mouse_click,
      on_move=self.on_mouse_move,
      on_scroll=self.on_mouse_scroll,
    )
    self.mouse_listener.start()
    self.sketch_listener = self.subscribe('sketch_did_stop', lambda sketch: self.reset_sketch())

  def on_key_press(self, key):
    parsed_key = parse_key(key)
    if self.commands is not None:
      if self.autocomplete.active:
        if self.autocomplete.pause_key == parsed_key:
          self.autocomplete.active = False
        else:
          self.autocomplete.on_key_press(parsed_key)
      elif self.autocomplete.pause_key == parsed_key:
        self.autocomplete.active = True
    
    self.keys[key] = True
    if self.sketch:
      self.sketch.on_key_press(parsed_key)

  def on_key_release(self, key):
    parsed_key = parse_key(key)
    self.keys[parsed_key] = False
    if self.sketch:
      self.sketch.on_key_release(parsed_key)

  def is_key_pressed(self, key):
    return key in self.keys and self.keys[key]

  def on_mouse_click(self, x, y, button, pressed):
    parsed_button = button._name_
    self.buttons[parsed_button] = pressed
    if self.sketch:
      if pressed:
        self.sketch.on_mouse_press(parsed_button)
      else:
        self.sketch.on_mouse_release(parsed_button)

  def on_mouse_move(self, x, y):
    self.mouse_position = (x, y)
    if self.sketch:
      self.sketch.on_mouse_move(self.mouse_position)

  def on_mouse_scroll(self, x, y, dx, dy):
    if self.sketch:
      self.sketch.on_mouse_scroll((dx, dy))

  def is_button_pressed(self, button):
    return button in self.buttons and self.buttons[button]

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
    if 'sketch' in self.__dict__ and self.sketch and self.sketch.alive:
      self.sketch.stop()
    if 'autocomplete' not in self.__dict__:
      self.autocomplete = Autocomplete()
      self.autocomplete.setup_with_controller(self)
    self.sketch = None

  def run_sketch(self, Sketch):
    if Sketch.connect is True:
      self.connect()

    self.sketch = Sketch()
    self.sketch.setup_with_controller(self)

  def reset_commands(self):
    self.commands = None

  def use_commands(self, pause_key='pause', accept_key='enter', delete_key='backspace', load=False):
    self.commands = {}
    self.stored_sketch = None
    if load:
      if 'command_keys' in self.configuration:
        self.autocomplete.pause_key = self.configuration['command_keys']['pause']
        self.autocomplete.accept_key = self.configuration['command_keys']['accept']
        self.autocomplete.delete_key = self.configuration['command_keys']['delete']
      else:
        raise ControllerError('Define command_keys in config file when using load flag')
    else:
      self.autocomplete.pause_key = pause_key
      self.autocomplete.accept_key = accept_key
      self.autocomplete.delete_key = delete_key

  def add_command(self, command, callback):
    if self.commands is not None:
      if not command in self.commands:
        self.commands[command] = callback
      else:
        raise ControllerError(f'Command {command} is already set')
    else:
      raise ControllerError('Enable commands using use_commands method')

  def set_commands(self, commands):
    if self.commands is not None:
      if isinstance(commands, dict):
        self.commands = commands
      else:
        raise ControllerError('Passed commands should be in dictionary')
    else:
      raise ControllerError('Enable commands using use_commands method')

  def loop(self):
    if self.commands is not None:
      while self.alive:
        if self.sketch is not None:
          self.sketch.update()
        if self.sketch is not None:
          self.sketch.render()
        else:
          self.autocomplete.render()

        for device in self.devices: # TODO Autocomplete should render devices on its own
          device.render()

        if self.sketch is not None:
          time.sleep(self.sketch.interval)
        else:
          time.sleep(self.autocomplete.interval)

    elif self.sketch is not None:
      while self.sketch:
        self.sketch.update()
        if self.sketch:
          self.sketch.render()

          for device in self.devices:
            device.render()

          time.sleep(self.sketch.interval)