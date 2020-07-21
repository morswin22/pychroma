<h1 align="center">
  pychroma
<h1>

<p align="center">
  <a href="https://github.com/morswin22/pychroma/blob/master/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/morswin22/pychroma">
  </a>
  <a href="https://www.python.org/downloads/">
    <img alt="Python" src="https://img.shields.io/pypi/pyversions/pychroma">
  </a>
  <a href="https://pypi.org/project/pychroma/">
    <img alt="Version" src="https://img.shields.io/pypi/v/pychroma">
  </a>
</p>

<h3 align="center">
  Python library for accessing the Razer Chroma SDK
</h3>

pychroma provides general-purpose access to the [Razer Chroma SDK REST API](https://assets.razerzone.com/dev_portal/REST/html/index.html) for control over the LEDs of Razer devices. 
The work environment is easy to set up and it features a sketch and (optionally) a controller. The sketch code structure is heavily inspired from [p5js.org](https://p5js.org/) conventions. The controller allows having multiple sketches.

### Features

* Full controll over the LEDs via Chroma SDK
* Low barrier to entry for educators and practitioners

Made for everyone

* Simply use the sketch! This library is accessible and inclusive for artists, designers, educators and beginners
* Gain more access by using the controller or handling the connection and devices all by yourself
* If you want to have full control then fork this repository and edit the source code

## Installation

This repo is tested on Python 3.8.3, requests 2.23.0 and pynput 1.6.8

### With pip
pychroma can be installed using pip as follows:
```bash
pip install pychroma
```

### From source
You can install from source by cloning the repository and running:
```bash
git clone https://github.com/morswin22/pychroma
cd pychroma
pip install .
```

When you update the repository, you should upgrade the pychroma installation and its dependencies as follows:
```bash
git pull
pip install --upgrade .
```

### Run the examples
You can download the examples from the [examples repo](https://github.com/morswin22/pychroma-examples)

Look at the README included with examples for more information

### Tests
A series of tests are included for the library. Library tests can be found in the tests folder.

Here's the easiest way to run tests for the library:
```bash
python -m unittest discover -v -s ./tests -p test*.py
```

If you are using Visual Studio Code then you can use it's built in testing with python add-on

## Quick Tour
Check out the [wiki](https://github.com/morswin22/pychroma/wiki) for detailed documentation.

Create a configuration file in JSON format.
```json
{
  "chroma": {
    "developerName": "Your name",
    "developerContact": "Your email",
    "category": "application",
    "supportedDevices": ["keyboard"],
    "description": "Basic hello world sketch",
    "title": "Hello world!"
  }
}
```

### Creating a sketch
```python
from pychroma import Sketch

class MySketch(Sketch):
  config_path = 'path/to/config/file.json'
```

### Example animation code
```python
from pychroma import Sketch

class MySketch(Sketch):
  config_path = 'path/to/config/file.json'

  def setup(self):
    self.frame_rate = 30
    self.keyboard.color_mode('hsv')
    self.hue = 0
    
  def update(self):
    self.hue += 1
    if self.hue == 360:
      self.stop()
    
  def render(self):
    self.keyboard.set_static((self.hue, 100, 100))
```
