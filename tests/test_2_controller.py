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
      controller.subscribe('sketch_did_stop', lambda sketch: self.assertEqual(sketch.hue, 360), time_to_live=1)

  def test_commands(self):
    with Controller('./tests/assets/example.json') as controller:
      keys = (('pause', 'enter', 'backspace'),('a', 'b', 'c'),('num_1', 'num_2', 'num_3'))
      for index, (pause_key, accept_key, delete_key) in enumerate(keys):
        if index == 0:
          controller.use_commands()
        elif index == 1:
          controller.use_commands(delete_key=delete_key, pause_key=pause_key, accept_key=accept_key)
        elif index == 2:
          controller.use_commands(load=True)

        self.assertIsInstance(controller.commands, dict)

        self.assertEqual(controller.autocomplete.pause_key, pause_key)
        self.assertEqual(controller.autocomplete.accept_key, accept_key)
        self.assertEqual(controller.autocomplete.delete_key, delete_key)

        controller.reset_commands()
        self.assertIsNone(controller.commands)

      controller.stop()