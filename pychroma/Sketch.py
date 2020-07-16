class Sketch:
  def __init__(self):
    self.frame_rate = None

  def setup_with_controller(self, controller):
    self.controller = controller
    self.setup_devices(self.controller.devices)
    self.setup()

  def setup_devices(self, devices):
    for device in devices:
      self.__dict__[device.name] = device
      device.clear()
      device.set_none()

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
