class Sketch:
  def __init__(self, controller):
    self.controller = controller
    for device in controller.devices:
      self.__dict__[device.name] = device
      device.clear()
      device.set_none()
    self.frame_rate = None

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
