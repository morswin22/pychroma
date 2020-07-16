import json
import unittest

from pychroma import Connection, Device, DeviceError, parse_rgb


class DeviceTest(unittest.TestCase):
  def setUp(self):
    with open('./tests/assets/example.json', 'r') as file:
      config = json.load(file)

    self.connection = Connection(config['chroma'])

  def tearDown(self):
    self.connection.stop()

  def test_valid_devices(self):
    for device_name in Device.TYPES['grid'] + Device.TYPES['array']:
      Device(self.connection.url, device_name)

  def test_invalid_devices(self):
    for device_name in Device.TYPES['grid'] + Device.TYPES['array']:
      with self.assertRaises(DeviceError) as error:
        Device(self.connection.url, device_name[::-1])

      self.assertEqual(str(error.exception), "Unknown device type")

  def test_device_size(self):
    for device_name in Device.TYPES['grid'] + Device.TYPES['array']:
      device = Device(self.connection.url, device_name)

      self.assertTrue(device.type in Device.TYPES)

      if device.type == 'array':
        self.assertTrue(isinstance(device.size, int))
      elif device.type == 'grid':
        self.assertTrue(isinstance(device.size, tuple))
  
  def test_in_bounds(self):
    for device_name in Device.TYPES['grid'] + Device.TYPES['array']:
      device = Device(self.connection.url, device_name)

      if device.type == 'array':
        with self.assertRaises(DeviceError) as error:
          device.set_grid((0,0), (0,0,0))
        
        self.assertEqual(str(error.exception), "Can not check is in grid on non-grid device")
        
        for pos in range(device.size):
          self.assertTrue(device.in_array(pos))

        for invalid_pos in [-1, device.size, device.size + 1]:
          self.assertFalse(device.in_array(invalid_pos))

          with self.assertRaises(DeviceError) as error:
            device.set_array(invalid_pos, (0,0,0))

          self.assertEqual(str(error.exception), "Position out of array bounds")

      elif device.type == 'grid':
        with self.assertRaises(DeviceError) as error:
          device.set_array(0, (0,0,0))
        
        self.assertEqual(str(error.exception), "Can not check is in array on non-array device")
        
        for x in range(device.size[0]):
          for y in range(device.size[1]):
            self.assertTrue(device.in_grid((x, y)))

        for invalid_pos in [(-1, 0), (0, -1), (device.size[0], 0), (0, device.size[1]), (device.size[0] + 1, 0), (0, device.size[1] + 1)]:
          self.assertFalse(device.in_grid(invalid_pos))

          with self.assertRaises(DeviceError) as error:
            device.set_grid(invalid_pos, (0,0,0))

          self.assertEqual(str(error.exception), "Position out of grid bounds")

  def test_parse_color(self):
    invalid_colors = {
      'hsv': [(0, -1, 0), (0, 0, 101), '#333333', (0, 0), (0, 0, 0, 0)],
      'hsv-normalized': [(0, -1, 0), (0, 0, 2), '#333333', (0, 0), (0, 0, 0, 0)],
      'rgb': [(-1, 0, 0), (0, 256, 0), '#333333', (0, 0), (0, 0, 0, 0)],
      'rgb-normalized': [(-1, 0, 0), (0, 2, 0), '#333333', (0, 0), (0, 0, 0, 0)],
      'hex': [(0,), '#1234567', '#12345', '#gggggg'],
    }

    for color_mode in invalid_colors:
      parse_fn = Device.COLOR_MODES[0][color_mode]

      for invalid_color in invalid_colors[color_mode]:
        with self.assertRaises(DeviceError) as error:
          parse_fn(invalid_color)
      
        self.assertEqual(str(error.exception), "Can not parse inserted color")
    
    valid_colors = {
      'hsv': [(0, 0, 0), (180, 50, 50), (360, 100, 100)],
      'hsv-normalized': [(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
      'rgb': [(0, 0, 0), (128, 128, 128), (255, 255, 255)],
      'rgb-normalized': [(0, 0, 0), (0.5, 0.5, 0.5), (1, 1, 1)],
      'hex': ['#000000', '#888888', '#ffffff'],
    }

    for color_mode in valid_colors:
      parse_fn = Device.COLOR_MODES[0][color_mode]

      for valid_color in valid_colors[color_mode]:
        self.assertTrue(isinstance(parse_fn(valid_color), int)) 

  def test_state(self):
    for device_name in Device.TYPES['grid'] + Device.TYPES['array']:
      device = Device(self.connection.url, device_name)

      device.set_none()
      self.assertEqual(device.state, 'NONE')

      device.set_static((0,0,0))
      self.assertEqual(device.state, 'STATIC')

      if device.type == 'array':
        device.set_array(0, (0,0,0))
      elif device.type == 'grid':
        device.set_grid((0,0), (0,0,0))
      
      self.assertEqual(device.state, 'CUSTOM')

  def test_fill_and_clear(self):
    for device_name in Device.TYPES['grid'] + Device.TYPES['array']:
      device = Device(self.connection.url, device_name)

      if device.type == 'array':
        for pos in range(device.size):
          device.set_array(pos, (127, 127, 127))
          self.assertEqual(device.array[pos], parse_rgb((127, 127, 127)))

        device.clear()

        for pos in range(device.size):
          self.assertEqual(device.array[pos], 0)

      elif device.type == 'grid':
        for x in range(device.size[0]):
          for y in range(device.size[1]):
            device.set_grid((x, y), (127, 127, 127))
            self.assertEqual(device.grid[y][x], parse_rgb((127, 127, 127)))

        device.clear()

        for x in range(device.size[0]):
          for y in range(device.size[1]):
            self.assertEqual(device.grid[y][x], 0)
