import colorsys
import struct

import numpy as np
import pyaudio
from scipy.fftpack import fft

from Sketch import Sketch

def sigmoid(x):
  return 1 / (1 + np.e**-x)

def hsv2rgb(h,s,v):
  return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

class Equalizer(Sketch):
  def setup(self):
    self.frame_rate = 1/12
    self.height = len(self.keyboard.grid)
    self.width = len(self.keyboard.grid[0])
    self.CHUNK = 2048
    self.bars = []
    self.theta = 0
    self.dtheta = 0.03

    device = self.controller.get_audio_mix()

    if device != None:
      self.FORMAT = pyaudio.paInt16
      self.CHANNELS = int(device['maxInputChannels'])
      self.RATE = int(device['defaultSampleRate'])
      self.MAX_y = 2.0**(self.controller.audio.get_sample_size(self.FORMAT) * 8 - 1)
      self.stream = self.controller.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, input_device_index=device['index'], frames_per_buffer=self.CHUNK)
    else:
      print('Stereo mix not found')
      self.controller.soft(self.controller.idle)

  def update(self):
    N = max(self.stream.get_read_available() / self.CHUNK, 1) * self.CHUNK
    data = self.stream.read(int(N))

    y = np.array(struct.unpack("%dh" % (N * self.CHANNELS), data)) / self.MAX_y
    y_L = fft(y[::2], self.CHUNK)
    y_R = fft(y[1::2], self.CHUNK)

    Y = abs(np.hstack((y_L[int(-self.CHUNK / 2):-1], y_R[:int(self.CHUNK / 2)]))) # Both Center
    # Y = abs(np.hstack((y_L[-1:int(-self.CHUNK / 2):-1], y_R[int(self.CHUNK / 2)::-1]))) # Left & Right
    len_Y = len(Y)

    self.bars = []
    step = round(len_Y / self.width)
    for i in range(self.width):
      start = i * step
      stop = min((i+1) * step, len_Y)
      bar = round(((sigmoid(sum(Y[start:stop]) / (stop-start)) / 5) - .1) * 10 * self.height)
      self.bars.append(bar)

    self.theta = (self.theta + self.dtheta) % 1

  def render(self):
    for y in range(self.height):
      for x in range(self.width):
        if y > self.height - self.bars[x] - 1:
          color = hsv2rgb((self.theta - x * 0.02) % 1, .95, 1)
          self.keyboard.grid[y][x].set(red=color[0], green=color[1], blue=color[2])
        else:
          self.keyboard.grid[y][x].set(red=0, green=0, blue=0)
