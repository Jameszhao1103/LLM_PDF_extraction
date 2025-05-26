import json
import os
import unittest
from src.json_handler import JSONHandler

class TestJSONHandler(unittest.TestCase):
    def setUp(self):
        self.json_handler = JSONHandler()
        self.test_data = {"key": "value"}
        self.test_file = 'test_output.json'

    def test_save_to_json(self):
        self.json_handler.save_to_json(self.test_data, self.test_file)
        self.assertTrue(os.path.exists(self.test_file))

    def test_load_from_json(self):
        self.json_handler.save_to_json(self.test_data, self.test_file)
        loaded_data = self.json_handler.load_from_json(self.test_file)
        self.assertEqual(loaded_data, self.test_data)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

if __name__ == '__main__':
    unittest.main()