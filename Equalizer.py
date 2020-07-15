import struct

import numpy as np
import pyaudio
from scipy.fftpack import fft

from pychroma import Sketch


def sigmoid(x):
  return 1 / (1 + np.e**-x)

def get_audio_mix(audio, audio_info):
  for i in range(audio.get_device_count()):
    device = audio.get_device_info_by_index(i)
    if device['name'] == audio_info['name'] and device['hostApi'] == audio_info['hostApi']:
      return device
  return None

class Equalizer(Sketch):
  def setup(self):
    self.frame_rate = 1/12
    self.keyboard.color_mode('hsv-normalized')
    self.mouse.color_mode('hsv-normalized')
    self.width, self.height = self.keyboard.size
    self.mouse_height = self.mouse.size[1]
    self.CHUNK = 2048
    self.bars = []
    self.volume = (0,0)
    self.max_volume = 1
    self.theta = 0
    self.dtheta = 0.03

    self.audio = pyaudio.PyAudio()
    device = get_audio_mix(self.audio, self.controller.misc_info['audio'])

    if device != None:
      self.FORMAT = pyaudio.paInt16
      self.CHANNELS = int(device['maxInputChannels'])
      self.RATE = int(device['defaultSampleRate'])
      self.MAX_y = 2.0**(self.audio.get_sample_size(self.FORMAT) * 8 - 1)
      self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, input_device_index=device['index'], frames_per_buffer=self.CHUNK)
    else:
      print('Stereo mix not found')
      self.controller.soft(self.controller.idle)

  def update(self):
    N = max(self.stream.get_read_available() / self.CHUNK, 1) * self.CHUNK
    data = self.stream.read(int(N))

    y = np.array(struct.unpack("%dh" % (N * self.CHANNELS), data)) / self.MAX_y
    y_L = fft(y[::2], self.CHUNK)[int(-self.CHUNK / 2):-1]
    y_R = fft(y[1::2], self.CHUNK)[:int(self.CHUNK / 2)]

    self.volume = (int(abs(sum(y_L)/len(y_L)**0.5)), int(abs(sum(y_R)/len(y_R)**0.5)))

    Y = abs(np.hstack((y_L, y_R))) # Both Center
    # Y = abs(np.hstack((y_L, y_R))) # Left & Right
    len_Y = len(Y)

    self.bars = []
    step = round(len_Y / self.width)
    for i in range(self.width):
      start = i * step
      stop = min((i+1) * step, len_Y)
      bar = round(((sigmoid(sum(Y[start:stop]) / (stop-start)) / 5) - .1) * 10 * self.height)
      self.bars.append(bar)

    self.theta += self.dtheta

  def render(self):
    for y in range(self.height):
      for x in range(self.width):
        if y > self.height - self.bars[x] - 1:
          self.keyboard.set_grid((x, y), (self.theta - x * 0.02, .95, 1))
        else:
          self.keyboard.set_grid((x, y), (0, 0, 0))
    for (x, value) in ((0, self.volume[0]), (6, self.volume[1])):
      if value > self.max_volume:
        self.max_volume = value
      diff = self.mouse_height - value / self.max_volume * 6 - 2
      for y in range(1, self.mouse_height):
        if y > diff:
          self.mouse.set_grid((x, y), (self.theta - y * 0.04 + 0.4, .95, 1))
        else:
          self.mouse.set_grid((x, y), (0, 0, 0))
    mean = sum(self.volume) / len(self.volume) / self.max_volume
    for y in (2, 7):
      self.mouse.set_grid((3, y), (self.theta - y * 0.04 + 0.4, .95, mean))
