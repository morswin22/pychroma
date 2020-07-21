import unittest

from pychroma import Controller, ControllerError, Device, Sketch


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
