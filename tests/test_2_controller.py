import unittest

from pychroma import Controller, ControllerError, Device, Sketch


class ControllerTest(unittest.TestCase):
  def test_devices(self):
    with Controller('./tests/assets/example.json') as controller:
      controller.connect()

      self.assertTrue(isinstance(controller.keyboard, Device))
      self.assertTrue(isinstance(controller.mouse, Device))
      self.assertTrue(isinstance(controller.mousepad, Device))
      self.assertTrue(isinstance(controller.keypad, Device))
      self.assertTrue(isinstance(controller.headset, Device))
      self.assertTrue(isinstance(controller.chromalink, Device))

      controller.quit()

  def test_sketch_integration(self):
    with Controller('./tests/assets/example.json') as controller:
      controller.run_sketch(Sketch)

      self.assertTrue(isinstance(controller.sketch, Sketch))
      temp = controller.sketch

      controller.store_sketch()

      self.assertEqual(controller.stored_sketch, temp)

      controller.restore_sketch()

      self.assertEqual(controller.sketch, temp)
      self.assertEqual(controller.stored_sketch, None)

      controller.idle()

      self.assertFalse(isinstance(controller.sketch, Sketch))

      controller.quit()