import json
import unittest

from pychroma import Connection, ConnectionError


class ConnectionTest(unittest.TestCase):
  def test_wrong_connection_data(self):
    with self.assertRaises(ConnectionError) as error, open('./tests/assets/example.json', 'r') as file:
      config = json.load(file)
      del config['chroma'][list(config['chroma'])[0]]
      Connection(config['chroma'])

    self.assertEqual(str(error.exception), "Invalid data structure")

  def test_valid_connection(self):
    with open('./tests/assets/example.json', 'r') as file:
      config = json.load(file)

    connection = Connection(config['chroma'])
    self.assertTrue(connection.alive)

    self.assertFalse(connection.is_connected())
    self.assertIsNone(connection.url)
    self.assertIsNone(connection.heartbeat_url)
    
    connection.connect()

    self.assertTrue(connection.is_connected())
    self.assertRegex(connection.url, r"http://localhost:[0-9]+/chromasdk")
    self.assertRegex(connection.heartbeat_url, r"http://localhost:[0-9]+/chromasdk/heartbeat")

    connection.disconnect()

    self.assertFalse(connection.is_connected())
    self.assertIsNone(connection.url)
    self.assertIsNone(connection.heartbeat_url)

    connection.stop()

    self.assertFalse(connection.alive)
