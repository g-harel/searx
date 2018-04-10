import sys
from searx.DatabaseHandler import TinyDatabase, MongoDatabase, Database
from searx import ConsistencyChecker
from searx.testing import SearxTestCase
from mock import MagicMock
from searx import search
from mock import Mock, mock, patch
import requests


class TestTopTen(SearxTestCase):
    def test_top_ten_functionality(self):
        mocked_tinydb = TinyDatabase()
        mocked_tinydb.connect = MagicMock()
        mocked_tinydb.load_all = MagicMock(return_value=[
            {'query': 'how to test forklift',
                'time': '2018-03-25 21:20:38'},
            {'query': 'how to test forklift',
                'time': '2018-03-25 21:20:39'},
            {'query': 'how to test forklift',
                'time': '2018-03-25 21:20:40'},
            {'query': 'how much calory does water have',
                'time': '2018-03-25 10:20:38'},
            {'query': 'is gullible in the dictionary',
                'time': '2018-03-25 11:20:38'}
        ])

        top_ten = dict(mocked_tinydb.return_topten())
        self.assertEqual(top_ten['how to test forklift'], 3)
        self.assertEqual(top_ten['how much calory does water have'], 1)
        self.assertEqual(top_ten['is gullible in the dictionary'], 1)

        mocked_tinydb.load_all.assert_any_call()

    def test_top_ten_with_no_queries(self):
        mocked_tinydb = TinyDatabase()
        mocked_tinydb.connect = MagicMock()
        mocked_tinydb.load_all = MagicMock()

        top_ten = dict(mocked_tinydb.return_topten())
        self.assertEqual(len(top_ten), 0)

    def test_top_ten_with_big_data(self):
        mocked_tinydb = TinyDatabase()
        mocked_tinydb.connect = MagicMock()
        mocked_tinydb.load_all = MagicMock(return_value=[
            {'query': 'how to test forklift',
             'time': '2019-03-25 21:20:38'},
            {'query': 'how to test forklift',
             'time': '2019-03-25 21:20:38'},
            {'query': 'how to test forklift2',
             'time': '2018-03-25 21:20:39'},
            {'query': 'how to test forklift2',
             'time': '2017-03-25 21:20:40'},
            {'query': 'how to test forklift2',
             'time': '2017-03-25 21:20:40'},
            {'query': 'how to test forklift4',
             'time': '2015-03-25 21:20:40'},
            {'query': 'how to test forklift3',
             'time': '2014-03-25 21:20:40'},
            {'query': 'how to test forklift5',
             'time': '2013-03-25 21:20:40'},
            {'query': 'how to test forklift6',
             'time': '2012-03-25 21:20:40'},
            {'query': 'how to test forklift7',
             'time': '2011-03-25 21:20:40'},
            {'query': 'how to test forklift8',
             'time': '2010-03-25 21:20:40'},
            {'query': 'how to test forklift9',
             'time': '2009-03-25 21:20:40'},
            {'query': 'how much calory does water have',
             'time': '2018-03-25 10:20:38'},
            {'query': 'is gullible in the dictionary',
             'time': '2018-03-25 11:20:38'}
        ])

        top_ten = dict(mocked_tinydb.return_topten())
        self.assertEqual(top_ten['how to test forklift'], 2)
        self.assertEqual(top_ten['how to test forklift2'], 3)
