from Controller import Controller
from Snake import *
from Hello import *

with Controller("config.json") as controller:
  controller.add_command('idle', controller.disconnect)
  controller.add_command('resume', controller.resume)
  controller.add_command('quit', controller.quit)
  controller.add_command('snake', controller.do_run(Snake))
  controller.run_sketch(Hello)
