# -*- coding: utf-8 -*-

from searx.DatabaseHandler import TinyDatabase, MongoDatabase, Database
from searx.testing import SearxTestCase

class DatabaseHandlerTestCase(SearxTestCase):
    def test_forklift_prepare_data(self):
        test_results = [
            {'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'},
            {'query': 'what is an elephant', 'time': '2018-03-25 21:20:39'},
            {'query': 'how to remove stains', 'time': '2018-03-25 21:20:40'},
            {'query': 'how much calory does water have', 'time': '2018-03-25 10:20:38'},
            {'query': 'is gullible in the dictionary', 'time': '2018-03-25 11:20:38'}
        ]

        for result in test_results:
            prepared_result = TinyDatabase.forklift_prepare_data(self, result)
            self.assertEqual(result, prepared_result)
