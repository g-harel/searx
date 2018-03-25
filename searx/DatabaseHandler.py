from tinydb import TinyDB, Query


class Database(object):
    def __init__(self):
        self.data = None
        self.db   = None

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
        User = Query()


class MongoDatabase(Database):
    def connect(self):
        pass






