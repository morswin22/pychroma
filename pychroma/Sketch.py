class SketchError(Exception):
  pass

class Sketch:
  config_path = None
  connect = True

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
    if 'devices' in self.controller.__dict__:
      self.setup_devices(self.controller.devices)
    self.setup()
    self.controller.emit('sketch_did_setup', self)

  def setup_devices(self, devices):
    for device in devices:
      self.__dict__[device.name] = device
      device.clear()
      device.color_mode('rgb')
      device.set_none()

  def stop(self):
    self.alive = False
    self.controller.emit('sketch_did_stop', self)

  def on_key_press(self, key):
    pass

  def on_key_release(self, key):
    pass

  def on_mouse_press(self, key):
    pass

  def on_mouse_release(self, key):
    pass

  def on_mouse_move(self, position):
    pass

  def on_mouse_scroll(self, delta):
    pass

  def setup(self):
    pass

  def update(self):
    pass

  def render(self):
    pass
