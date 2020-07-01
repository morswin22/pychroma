class Sketch:
  def __init__(self, controller):
    self.controller = controller
    self.keyboard = controller.keyboard
    self.mouse = controller.mouse
    self.mousepad = controller.mousepad
    for device in controller.devices:
      device.grid.clear()
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
