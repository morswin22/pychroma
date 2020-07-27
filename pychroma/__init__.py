import atexit
import sys
import inspect
import json
import time

from .Autocomplete import Autocomplete
from .Connection import Connection, ConnectionError
from .Controller import Controller, ControllerError, parse_key
from .Device import (Device, DeviceError, parse_hex, parse_hsv,
                     parse_hsv_normalized, parse_rgb, parse_rgb_normalized)
from .Sketch import Sketch, SketchError

def no_controller():
  if Controller.defined is False:
    sketches = []
    for name, obj in inspect.getmembers(sys.modules['__main__'], inspect.isclass):
      if (obj is not Sketch) and (Sketch in inspect.getmro(obj)):
        sketches.append((obj, name))
    
    num_sketches = len(sketches)
    if num_sketches == 0:
      raise SketchError('No sketches found')
    elif num_sketches == 1:
      sketch_class, sketch_name = sketches.pop()
      if sketch_class.config_path is not None:
        with Controller(sketch_class.config_path) as controller:
          controller.run_sketch(sketch_class)
      else:
        raise SketchError(f'When not using Controller define config_path in {sketch_name}')
    else:
      raise SketchError(f'Use Controller to run multiple sketches (found {num_sketches})')

atexit.register(no_controller)
