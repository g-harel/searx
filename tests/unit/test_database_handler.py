import sys
from searx.DatabaseHandler import TinyDatabase, MongoDatabase, Database
from searx import ConsistencyChecker
from searx.testing import SearxTestCase
from mock import MagicMock
from searx import search
from mock import Mock, mock, patch
import requests


def side_affect(self, arg):
    if arg == '2018-03-25 21:20:38':
        return {'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'}
    elif arg == '2019-03-25 21:20:38':
        {}
    else:
        return {}


class DatabaseHandlerTestCase(SearxTestCase):
    def test_forklift_prepare_data(self):
        test_results = [
            {'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'},
            {'query': 'what is an elephant', 'time': '2018-03-25 21:20:39'},
            {'query': 'how to remove stains', 'time': '2018-03-25 21:20:40'},
            {'query': 'how much calory does water have',
                'time': '2018-03-25 10:20:38'},
            {'query': 'is gullible in the dictionary',
                'time': '2018-03-25 11:20:38'}
        ]

    @mock.patch('searx.ConsistencyChecker.ConsistencyChecker')
    def test_shadow_write(self, mocked_checker):
        mongo = MongoDatabase()

        mongo.connect = MagicMock()
        mongo.prepare_data = MagicMock()
        mongo.insert = MagicMock()

        mongo.connect_prepare_and_insert_async({}, mocked_checker)

        self.assertTrue(mongo.connect.assert_called)
        mongo.prepare_data.assert_called_with({})
        self.assertTrue(mongo.insert.assert_called)
        self.assertTrue(mocked_checker.run.assert_called)

    @mock.patch('searx.ConsistencyChecker.ConsistencyChecker')
    def test_shadow_read(self, mocked_checker):
        mongo = MongoDatabase()

        mongo.connect = MagicMock()
        mongo.load_duplicates_count = MagicMock(return_value=[])
        mongo.verify_top_ten = MagicMock()

        mongo.connect_and_read_async([], mocked_checker)

        self.assertTrue(mongo.connect.assert_called)
        self.assertTrue(mongo.load_duplicates_count.assert_called)
        mongo.verify_top_ten.assert_called_with([], [])
        self.assertTrue(mocked_checker.run.assert_called)

    @mock.patch('searx.DatabaseHandler.TinyDatabase')
    @mock.patch('searx.DatabaseHandler.MongoDatabase')
    def test_forklift_execution(self, mocked_mongo, mocked_tinydb):
        mocked_tinydb.load_all.return_value = [
            {'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'}]

        db = TinyDatabase()
        db.forklift(mocked_tinydb, mocked_mongo)

        self.assertTrue(mocked_tinydb.connect.assert_called)
        self.assertTrue(mocked_tinydb.load_all.assert_called)

        self.assertTrue(mocked_mongo.connect.assert_called)
        self.assertTrue(mocked_mongo.delete_all.assert_called)
        mocked_mongo.prepare_data.assert_called_with(
            {'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'})
        self.assertTrue(mocked_mongo.insert.assert_called)

    def test_consistency_tester_consistent_data(self):
        mocked_mongo_insert = MongoDatabase
        mocked_mongo_load_all = MongoDatabase
        mocked_mongo_find = MongoDatabase
        mocked_mongo_update_mongo = MongoDatabase
        mocked_mongo_delete = MongoDatabase

        mocked_http_requests = requests

        mocked_tiny_load_all = TinyDatabase
        mocked_tiny_find = TinyDatabase

        mocked_mongo_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift',
                           'time': '2018-03-25 21:20:38'}])
        mocked_mongo_find.find = MagicMock(
            return_value={'query': 'how to test forklift',
                          'time': '2018-03-25 21:20:38'})
        mocked_mongo_update_mongo.update = MagicMock(
            return_value={'2018-03-25 21:20:38', 'hello', 'bye'})
        mocked_mongo_delete.delete = MagicMock(reture_value='done')
        mocked_mongo_insert.insert = MagicMock(return_value='done')

        mocked_http_requests.post = MagicMock(content={'content': "COOL"})

        mocked_tiny_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift',
                           'time': '2018-03-25 21:20:38'}])

        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()

        self.assertEquals(checker.inconsistencies, 0)
        self.assertEqual(checker.inconsistency_messages, [])

    def test_consistency_checker_missing_row_in_mongo(self):
        mocked_mongo_insert = MongoDatabase
        mocked_mongo_load_all = MongoDatabase
        mocked_mongo_find = MongoDatabase
        mocked_mongo_update_mongo = MongoDatabase
        mocked_mongo_delete = MongoDatabase
        mocked_mongo_prepare_data = MongoDatabase

        mocked_http_requests = requests

        mocked_tiny_load_all = TinyDatabase
        mocked_tiny_find = TinyDatabase

        mocked_mongo_delete.delete = MagicMock(reture_value='done')
        mocked_mongo_insert.insert = MagicMock(return_value='done')
        mocked_mongo_prepare_data.prepare_data = MagicMock(return_value='done')

        mocked_mongo_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift',
                           'time': '2018-03-25 21:20:38'}])
        mocked_mongo_find.find = MagicMock().side_effect = side_affect
        mocked_mongo_update_mongo.update_mongo = MagicMock(
            return_value={'2018-03-25 21:20:38', 'hello', 'bye'})

        mocked_http_requests.post = mock.Mock(content='COOL')

        mocked_tiny_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift',
                           'time': '2018-03-25 21:20:38'},
                          {'query': 'what is an elephant',
                           'time': '2018-03-55 21:22:39'}])
        mocked_tiny_find.find = MagicMock(
            return_value={'query': 'how to test forklift',
                          'time': '2018-03-25 21:20:38'})

        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()

        self.assertEquals(checker.inconsistencies, 1)
        self.assertIn('what is an elephant', checker.inconsistency_messages[0])
        self.assertIn('missing row in mongodb',
                      checker.inconsistency_messages[0])
        mocked_mongo_prepare_data.prepare_data.assert_called_with(
            {'query': 'what is an elephant', 'time': '2018-03-55 21:22:39'})

    def test_consistency_inconsistent_rows(self):
        mocked_mongo_insert = MongoDatabase
        mocked_mongo_load_all = MongoDatabase
        mocked_mongo_find = MongoDatabase
        mocked_mongo_update_mongo = MongoDatabase
        mocked_mongo_delete = MongoDatabase

        mocked_http_requests = requests

        mocked_tiny_load_all = TinyDatabase
        mocked_tiny_find = TinyDatabase

        mocked_mongo_delete.delete = MagicMock(return_valeu="done")
        mocked_mongo_insert.insert = MagicMock(return_value='done')

        mocked_mongo_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift',
                           'time': '2018-03-25 21:20:38'}])
        mocked_mongo_find.find = MagicMock(
            return_value={'query': 'how to test forklift',
                          'time': '2018-03-25 21:20:38'})
        mocked_mongo_update_mongo.update_mongo = MagicMock(
            return_value={'2018-03-25 21:20:38', 'hello', 'bye'})

        mocked_http_requests.post = mock.Mock(content='COOL')

        mocked_tiny_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift2',
                           'time': '2018-03-25 21:20:38'}])

        # after update lookup
        mocked_tiny_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift2',
                           'time': '2018-03-25 21:20:38'}])

        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()

        self.assertEquals(checker.inconsistencies, 1)
        self.assertIn('how to test forklift2',
                      checker.inconsistency_messages[0])
        mocked_mongo_update_mongo.update_mongo.assert_called_with(
            '2018-03-25 21:20:38', 'how to test forklift',
            'how to test forklift2')

    def test_inconsistencies_extra_row_in_mongodb(self):
        mocked_mongo_insert = MongoDatabase
        mocked_mongo_load_all = MongoDatabase
        mocked_mongo_find = MongoDatabase
        mocked_mongo_update_mongo = MongoDatabase
        mocked_mongo_delete = MongoDatabase

        mocked_http_requests = requests

        mocked_tiny_load_all = TinyDatabase
        mocked_tiny_find = TinyDatabase

        mocked_mongo_delete.delete = MagicMock(return_valeu="done")
        mocked_mongo_insert.insert = MagicMock(return_value='done')

        mocked_mongo_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift',
                           'time': '2018-03-25 21:20:38'},
                          {'query': 'how to test forklift2',
                           'time': '2019-03-25 21:20:38'}])
        mocked_mongo_find.find = MagicMock(
            return_value={'query': 'how to test forklift',
                          'time': '2018-03-25 21:20:38'})
        mocked_mongo_update_mongo.update_mongo = MagicMock(
            return_value={'2018-03-25 21:20:38', 'hello', 'bye'})

        mocked_http_requests.post = mock.Mock(content='COOL')

        mocked_tiny_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift2',
                           'time': '2018-03-25 21:20:38'}])

        # after update lookup
        mocked_tiny_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift',
                           'time': '2018-03-25 21:20:38'}])

        mocked_tiny_find.find = MagicMock().side_effect = side_affect

        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()

        self.assertEquals(checker.inconsistencies, 1)
        self.assertIn('extra row in mongo', checker.inconsistency_messages[0])
        mocked_mongo_delete.delete.assert_called_with(
            'how to test forklift2', '2019-03-25 21:20:38')
