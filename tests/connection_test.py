import json
import unittest

from pychroma import Connection, ConnectionError


class ConnectionTest(unittest.TestCase):
  def setUp(self):
    with open('./tests/assets/example.json', 'r') as file:
      config = json.load(file)

    self.connection = Connection(config['chroma'])

  def tearDown(self):
    self.connection.stop()

  def test_wrong_connection_data(self):
    with self.assertRaises(ConnectionError) as error, open('./tests/assets/example.json', 'r') as file:
      config = json.load(file)
      del config['chroma'][list(config['chroma'])[0]]
      Connection(config['chroma'])

    self.assertEqual(str(error.exception), "Invalid data structure")

  def test_received_url(self):
    self.assertRegex(self.connection.url, r"http://localhost:[0-9]+/chromasdk")
    self.assertRegex(self.connection.heartbeat_url, r"http://localhost:[0-9]+/chromasdk/heartbeat")
