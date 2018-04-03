from searx.DatabaseHandler import TinyDatabase, MongoDatabase, Database
from searx import ConsistencyChecker
from searx.testing import SearxTestCase
from mock import MagicMock
from searx import search
from mock import Mock, mock, patch
import requests

class DatabaseHandlerTestCase(SearxTestCase):
    def test_forklift_prepare_data(self):
        test_results = [
            {'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'},
            {'query': 'what is an elephant', 'time': '2018-03-25 21:20:39'},
            {'query': 'how to remove stains', 'time': '2018-03-25 21:20:40'},
            {'query': 'how much calory does water have', 'time': '2018-03-25 10:20:38'},
            {'query': 'is gullible in the dictionary', 'time': '2018-03-25 11:20:38'}
        ]


    def test_consistency_tester(self):
        mocked_mongo_insert = MongoDatabase
        mocked_mongo_load_all= MongoDatabase
        mocked_mongo_find    = MongoDatabase
        mocked_mongo_update_mongo = MongoDatabase

        mocked_http_requests = requests

        mocked_tiny_load_all = TinyDatabase

        mocked_mongo_insert.insert = MagicMock(return_value='done')
        mocked_mongo_load_all.load_all = MagicMock(return_value=[{'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'}])
        mocked_mongo_find.find = MagicMock(return_value={'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'})
        mocked_mongo_update_mongo.update = MagicMock(return_value={'2018-03-25 21:20:38', 'hello', 'bye'})

        mocked_http_requests.post = MagicMock(content={'content':"COOL"})
        mocked_tiny_load_all.load_all = MagicMock(return_value = [{'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'}])

        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()

        assert(checker.inconsistencies, 0)
        assert(checker.inconsistency_messages, None)
        assert(checker.output.content,"COOL")

    def test_consistency_checker_missing_row(self):
        mocked_mongo_insert = MongoDatabase
        mocked_mongo_load_all = MongoDatabase
        mocked_mongo_find = MongoDatabase
        mocked_mongo_update_mongo = MongoDatabase

        mocked_http_requests = requests

        mocked_tiny_load_all = TinyDatabase

        mocked_mongo_insert.insert = MagicMock(return_value='done')
        mocked_mongo_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'}])
        mocked_mongo_find.find = MagicMock(
            return_value={'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'})
        mocked_mongo_update_mongo.update = MagicMock(return_value={'2018-03-25 21:20:38', 'hello', 'bye'})

        mocked_http_requests.post = MagicMock(content={'content': "COOL"})
        mocked_tiny_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'},
                          {'query': 'what is an elephant', 'time': '2018-03-25 21:20:39'}])

        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()

        assert(checker.inconsistencies, 1)
        self.assertIn('what is an elephant', checker.inconsistency_messages[0])
        assert(checker.output.content, "COOL")

    def test_consistency_inconsistent(self):
        mocked_mongo_insert = MongoDatabase
        mocked_mongo_load_all = MongoDatabase
        mocked_mongo_find = MongoDatabase
        mocked_mongo_update_mongo = MongoDatabase

        mocked_http_requests = requests

        mocked_tiny_load_all = TinyDatabase

        mocked_mongo_insert.insert = MagicMock(return_value='done')
        mocked_mongo_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'}])
        mocked_mongo_find.find = MagicMock(
            return_value={'query': 'how to test forklift', 'time': '2018-03-25 21:20:38'})
        mocked_mongo_update_mongo.update = MagicMock(return_value={'2018-03-25 21:20:38', 'hello', 'bye'})

        mocked_http_requests.post = MagicMock(content={'content': "COOL"})
        mocked_tiny_load_all.load_all = MagicMock(
            return_value=[{'query': 'how to test forklift2', 'time': '2018-03-25 21:20:38'}])

        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()

        assert (checker.inconsistencies, 1)
        self.assertIn('how to test forklift2', checker.inconsistency_messages[0])
        assert (checker.output.content, "COOL")
