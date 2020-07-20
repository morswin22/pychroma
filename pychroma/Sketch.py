import atexit


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

  def on_restored(self):
    pass 

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

def NoController():
  import sys, inspect, json, time
  from .Controller import Controller
  from .Connection import Connection
  from .Device import Device

  sketches = []
  for name, obj in inspect.getmembers(sys.modules['__main__'], inspect.isclass):
    if (obj is not Sketch) and (Sketch in inspect.getmro(obj)):
      sketches.append((obj, name))
  
  if Controller.defined is False:
    num_sketches = len(sketches)
    if num_sketches == 0:
      raise SketchError('No sketches found')
    elif num_sketches == 1:
      sketch_class = sketches.pop()
      sketch = sketch_class[0]()
      if sketch.config_path is not None:
        with open(sketch.config_path, 'r') as file:
          config = json.load(file)

        connection = Connection(config['chroma'])
        connection.connect()

        devices = []
        for name in config['chroma']['supportedDevices']:
          devices.append(Device(connection.url, name))

        time.sleep(1.5)

        sketch.setup_devices(devices)
        sketch.setup()

        while sketch.alive:
          sketch.update()
          sketch.render()

          for device in devices:
            device.render()

          time.sleep(sketch.interval)

        connection.disconnect()
      else:
        raise SketchError(f'When not using Controller define config_path in {sketch_class[1]}')
    else:
      raise SketchError(f'Use Controller to handle multiple sketches (found {num_sketches})')

atexit.register(NoController)
