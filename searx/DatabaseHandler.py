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
        self.db = TinyDB('../db.json')
        self.User = Query()

    def forklift(self):
        tinydb  = TinyDatabase()
        mongodb = MongoDatabase()

        tinydb.connect()
        mongodb.connect()

        mongodb.delete_all()

        tinydb_results = tinydb.load_all()

        for result in tinydb_results:
            mongodb.prepare_data(self.forklift_prepare_data(result))
            mongodb.insert()

    def forklift_prepare_data(self, result):
        query = result.get('query')
        time = result.get('time')

        return {'query': query, 'time': time}

    def load_all(self):
        return self.db.all()

    def search(self ,name):
        return self.db.search(self.User.query == name)


class MongoDatabase(Database):
    def connect(self):
        self.User = MongoClient(
            "mongodb://user123:password123@ds249398.mlab.com:49398/searx").searx
        self.db = self.User.trending

    def load_all(self):
        return self.db.find({})

    def delete_all(self):
        self.db.delete_many({})

    def find(self, name):
        return self.db.trending.find({'time':name}, {time: 0, query: 1})

    def update_mongo(self, time, query):
        self.db.trending.findOneAndUpdate(
        {'time': time},
        {'query': query}
        )
