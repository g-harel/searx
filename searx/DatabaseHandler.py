from tinydb import TinyDB, Query
from pymongo import MongoClient


class Database(object):
    def __init__(self):
        self.data = None
        self.db = None

    def insert(self):
        self.db.insert(self.data)

    def connect(self):
        self.db = None

    def prepare_data(self, data):
        self.data = data

    def load_all(self):
        return self.db.all()


class TinyDatabase(Database):
    def connect(self):
        self.db = TinyDB('./db.json')
        self.User = Query()


class MongoDatabase(Database):
    def connect(self):
        self.User = MongoClient(
            "mongodb://user123:password123@ds249398.mlab.com:49398/searx").searx
        self.db = self.User.trending

    def load_all(self):
        return self.db.find({})

    def forklift(self):
        mongodb = MongoDatabase()
        tinydb  = TinyDatabase()

        mongodb.connect()
        tinydb.connect()

        mongo_results = mongodb.load_all()

        for result in mongo_results:
            query = result.get('query')
            time = result.get('time')

            tinydb.prepare_data({'query': query, 'time': time})
            tinydb.insert()


