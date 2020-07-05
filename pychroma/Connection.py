import threading
import time

import requests


class ConnectionError(Exception):
  pass

class Connection(threading.Thread):
  REQUIRED_CONNECTION_DATA = ["developerName","developerContact","category","supportedDevices","description","title"]

  def __init__(self, data):
    threading.Thread.__init__(self)

    self.alive = True
    self.timeout = 1
    self.base_url = 'http://localhost:54235/razer/chromasdk'

    validated = self.validate(data)
    if validated:
      self.url = self.connect(validated)
      self.heartbeat_url = self.url + '/heartbeat'
      self.start()
    else:
      raise ConnectionError('Invalid data structure')

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

  def connect(self, data):
    response = requests.post(self.base_url, json=data).json()
    return response['uri']

  def run(self):
    while self.alive:
      requests.put(self.heartbeat_url)
      time.sleep(self.timeout)

  def stop(self):
    self.alive = False
    requests.delete(self.url)
