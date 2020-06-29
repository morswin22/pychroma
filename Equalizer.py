import struct

import numpy as np
import pyaudio
from scipy.fftpack import fft

from Sketch import Sketch

def sigmoid(x):
  return 1 / (1 + np.e**-x)

class Equalizer(Sketch):
  def setup(self):
    self.controller.frame_rate = 1/30

    self.FORMAT = pyaudio.paInt16
    self.CHUNK = 256
    self.CHANNELS = 2
    self.RATE = 48000
    self.MAX_y = 2.0**(self.controller.audio.get_sample_size(self.FORMAT) * 8 - 1)
    self.BARS_N = 22

    self.bars = []

    device_index = None
    for i in range(self.controller.audio.get_device_count()):
      device = self.controller.audio.get_device_info_by_index(i)
      if device['name'] == 'Miks stereo (Realtek(R) Audio)' and device['hostApi'] == 3:
        device_index = device['index']

    if device_index != None:
      self.stream = self.controller.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, input_device_index=device_index, frames_per_buffer=self.CHUNK)
    else:
      print('Stereo mix not found')
      self.controller.quit()

  def update(self):
    N = max(self.stream.get_read_available() / self.CHUNK, 1) * self.CHUNK
    data = self.stream.read(int(N))

    y = np.array(struct.unpack("%dh" % (N * self.CHANNELS), data)) / self.MAX_y
    y_L = fft(y[::2], self.CHUNK)
    y_R = fft(y[1::2], self.CHUNK)

    Y = abs(np.hstack((y_L[int(-self.CHUNK / 2):-1], y_R[:int(self.CHUNK / 2)])))

    self.bars = []
    step = round(self.CHUNK/self.BARS_N)
    for i in range(self.BARS_N):
      start = i * step
      stop = min((i+1) * step, self.CHUNK)
      bar = round(((sigmoid(sum(Y[start:stop]) / (stop-start)) / 5) - .1) * 50)
      self.bars.append(bar)

  def render(self):
    for y in range(5):
      for x in range(22):
        self.keyboard.grid[y][x].set(red=0, green=0, blue=0)
    for (x, ys) in enumerate(self.bars):
      for y in range(5, int(5 - ys), -1):
        self.keyboard.grid[y][x].set(red=0, green=255, blue=0)
