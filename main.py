from Controller import Controller
from Equalizer import *
from Hello import *
from Snake import *

with Controller("config.json") as controller:
  controller.add_command('', controller.idle)
  controller.add_command('exit', controller.quit)
  controller.add_command('snake', controller.do_run(Snake))
  controller.add_command('music', controller.do_run(Equalizer))
  controller.run_sketch(Hello)
