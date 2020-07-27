class SketchError(Exception):
  pass

class Sketch:
  config_path = None

  def __init__(self):
    self.frame_rate = 10
    self.alive = True

  @property
  def frame_rate(self):
    return 1 / self.interval

  @frame_rate.setter
  def frame_rate(self, value):
    self.interval = 1 / value

  def setup_with_controller(self, controller):
    self.controller = controller
    self.setup_devices(self.controller.devices)
    self.setup()

  def setup_devices(self, devices):
    for device in devices:
      self.__dict__[device.name] = device
      device.clear()
      device.set_none()

  def stop(self):
    self.alive = False

  def on_key_press(self, key):
    pass

  def on_key_release(self, key):
    pass

  def setup(self):
    pass

  def update(self):
    pass

  def render(self):
    pass
