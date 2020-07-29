import unittest

from pychroma import Controller, ControllerError, Device, Sketch


class Example(Sketch):
  def setup(self):
    self.frame_rate = 30
    self.hue = 0
    for device in self.controller.devices:
      device.color_mode('hsv')
    
  def update(self):
    self.hue += 2
    if self.hue == 360:
      self.stop()
    
  def render(self):
    color = (self.hue, 100, 100)
    for device in self.controller.devices:
      device.set_static(color)

class ControllerTest(unittest.TestCase):
  def test_devices(self):
    with Controller('./tests/assets/example.json') as controller:
      controller.connect()

      for device_name in ['keyboard', 'mouse', 'mousepad', 'keypad', 'headset', 'chromalink']:
        device = None
        for dev in controller.devices:
          if dev.name == device_name:
            device = dev
            break
        
        self.assertIsNotNone(device)
        self.assertTrue(isinstance(device, Device))

  def test_sketch(self):
    with Controller('./tests/assets/example.json') as controller:
      controller.run_sketch(Example)

      self.assertEqual(controller.sketch.hue, 360)