import colorsys

import requests


class DeviceError(Exception):
  pass

def parse_hsv(color):
  if isinstance(color, (list, tuple)) and len(color) == 3:
    if min(color[1:]) >= 0 and max(color[1:]) <= 100:
      color = colorsys.hsv_to_rgb(color[0] / 360, color[1] / 100, color[2] / 100)
      return (int(color[2]*255)<<16)|(int(color[1]*255)<<8)|int(color[0]*255)
    else:
      raise DeviceError('Can not parse inserted color')
  else:
    raise DeviceError('Can not parse inserted color')

def parse_hsv_normalized(color):
  if isinstance(color, (list, tuple)) and len(color) == 3:
    if min(color[1:]) >= 0 and max(color[1:]) <= 1:
      color = colorsys.hsv_to_rgb(color[0], color[1], color[2])
      return (int(color[2]*255)<<16)|(int(color[1]*255)<<8)|int(color[0]*255)
    else:
      raise DeviceError('Can not parse inserted color')
  else:
    raise DeviceError('Can not parse inserted color')

def parse_rgb(color):
  if isinstance(color, (list, tuple)) and len(color) == 3:
    if min(color) >= 0 and max(color) <= 255:
      return (int(color[2])<<16)|(int(color[1])<<8)|int(color[0])
    else:
      raise DeviceError('Can not parse inserted color')
  else:
    raise DeviceError('Can not parse inserted color')

def parse_rgb_normalized(color):
  if isinstance(color, (list, tuple)) and len(color) == 3:
    if min(color) >= 0 and max(color) <= 1:
      return (int(color[2]*255)<<16)|(int(color[1]*255)<<8)|int(color[0]*255)
    else:
      raise DeviceError('Can not parse inserted color')
  else:
    raise DeviceError('Can not parse inserted color')

def parse_hex(color):
  if isinstance(color, str) and 5 < len(color) < 8:
    try:
      return (int(color[-2:], base=16)<<16)|(int(color[-4:-2], base=16)<<8)|int(color[-6:-4], base=16)
    except ValueError:
      raise DeviceError('Can not parse inserted color')
  else:
    raise DeviceError('Can not parse inserted color')

class Device:
  COLOR_MODES = {
    'hsv': parse_hsv, 
    'hsv-normalized': parse_hsv_normalized, 
    'rgb': parse_rgb, 
    'rgb-normalized': parse_rgb_normalized, 
    'hex': parse_hex
  }
  TYPES = {
    'grid': ['keyboard', 'mouse', 'keypad'],
    'array': ['mousepad', 'headset', 'chromalink']
  }
  KEYBOARD_GRID = (22, 6)
  MOUSE_GRID = (7, 9)
  KEYPAD_GRID = (5, 4)
  MOUSEPAD_ARRAY = 20
  HEADSET_ARRAY = 5
  CHROMALINK_ARRAY = 5

  def __init__(self, url, name, config={}):
    self.name = name.lower()
    self.url = f"{url}/{self.name}"
    self.type = self.get_type()
    self.size = Device.__dict__[f"{name.upper()}_{self.type.upper()}"]
    self.color_mode('rgb')
    self.clear()
    self.map(config)
    self.set_none()

  def get_type(self):
    for dtype in Device.TYPES:
      if self.name in Device.TYPES[dtype]:
        return dtype
    raise DeviceError('Unknown device type')

  def clear(self):
    if self.type == 'grid':
      self.grid = []
      for i in range(self.size[1]):
        row = []
        for j in range(self.size[0]):
          row.append(0)
        self.grid.append(row)
    elif self.type == 'array':
      self.array = []
      for i in range(self.size):
        self.array.append(0)

  def set_none(self):
    self.state = 'NONE'

  def set_static(self, color):
    self.state = 'STATIC'
    self.color = self.parse_color(color)

  def in_grid(self, pos):
    if self.type == 'grid':
      return 0 <= pos[0] < self.size[0] and 0 <= pos[1] < self.size[1]
    else:
      raise DeviceError('Can not check is in grid on non-grid device')

  def set_grid(self, pos, color):
    if self.in_grid(pos):
      self.state = 'CUSTOM'
      self.grid[pos[1]][pos[0]] = self.parse_color(color)
    else:
      raise DeviceError('Position out of grid bounds')

  def in_array(self, pos):
    if self.type == 'array':
      return 0 <= pos < self.size
    else:
      raise DeviceError('Can not check is in array on non-array device')

  def set_array(self, pos, color):
    if self.in_array(pos):
      self.state = 'CUSTOM'
      self.array[pos] = self.parse_color(color)
    else:
      raise DeviceError('Position out of array bounds')

  def color_mode(self, mode):
    if mode in self.COLOR_MODES:
      self.parse_color = self.COLOR_MODES[mode]
    else:
      raise DeviceError('Unknown color mode')

  def map(self, config):
    if len(list(config)) > 0:
      self.mapped = config
    else:
      self.mapped = None

  def set_mapped(self, name, color, range=None):
    if self.mapped is not None:
      if name in self.mapped:
        pos = self.mapped[name]
        if isinstance(pos, list):
          self.set_grid(pos, color)
        elif isinstance(pos, int):
          self.set_array(pos, color)
        elif isinstance(pos, dict):
          if range is None:
            pass # TODO set for all members of range
          else:
            pass # TODO set for selected members by given range
        else:
          raise DeviceError('Mapped value should be a position or a range')
      else:
        raise DeviceError('Unkown mapping position')
    else:
      raise DeviceError('Unknown device mapping, specify your device name')

  def render(self):
    data = {"effect": "CHROMA_"+self.state}
    if self.name == 'mouse':
      data['effect'] += '2'
    if self.state == 'STATIC':
      data['param'] = {'color': self.color}
    elif self.state == 'CUSTOM':
      if self.type == 'grid':
        data['param'] = self.grid
      elif self.type == 'array':
        data['param'] = self.array
    requests.put(self.url, json=data)
