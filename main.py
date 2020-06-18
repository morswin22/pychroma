from ChromaPython import ChromaApp, ChromaAppInfo
from Controller import Controller
from Sketch import *

FRAME_RATE = 1/10

info = ChromaAppInfo()
info.DeveloperName = 'Patryk Janiak'
info.DeveloperContact = 'xmorswinx@gmail.com'
info.Category = 'application'
info.SupportedDevices = ['keyboard', 'mouse', 'mousepad']
info.Description = 'Custom lighting'
info.Title = 'Chroma'

app = ChromaApp(info)

controller = Controller(app, info, FRAME_RATE)
controller.run(Sketch)
