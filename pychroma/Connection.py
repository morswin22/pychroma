import threading
import time

import requests


class ConnectionError(Exception):
  pass

class Connection(threading.Thread):
  REQUIRED_CONNECTION_DATA = ["developerName","developerContact","category","supportedDevices","description","title"]

  def __init__(self, data):
    threading.Thread.__init__(self)

    self.base_url = 'http://localhost:54235/razer/chromasdk'
    self.alive = True
    self.url = None
    self.heartbeat_url = None
    self.timeout = 1

    self.validated = self.validate(data)
    if self.validated is not None:
      self.start()
    else:
      raise ConnectionError('Invalid data structure')

  def stop(self):
    self.alive = False
    if self.is_connected():
      self.disconnect()

  def is_connected(self):
    return self.url is not None

  def validate(self, data):
    for key in self.REQUIRED_CONNECTION_DATA:
      if not key in data:
        return None
    return {
      "title": data['title'],
      "description": data['description'],
      "author": {
        "name": data['developerName'],
        "contact": data['developerContact']
      },
      "device_supported": data['supportedDevices'],
      "category": data['category']
    }

  def connect(self):
    response = requests.post(self.base_url, json=self.validated).json()
    if isinstance(response, dict):
      self.url = response['uri']
      self.heartbeat_url = self.url + '/heartbeat'
    else:
      self.url = None
      self.heartbeat_url = None
      self.alive = False
      raise ConnectionError(response)

  def run(self):
    while self.alive:
      if self.is_connected():
        requests.put(self.heartbeat_url)
      time.sleep(self.timeout)

  def disconnect(self):
    requests.delete(self.url)
    self.url = None
    self.heartbeat_url = None

  def __del__(self):
    self.stop()
