from tinydb import TinyDB, Query
from pymongo import MongoClient
from collections import Counter
import ConsistencyChecker

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

    def connect_prepare_and_insert_async(self, data):
        self.connect()
        self.prepare_data(data)
        self.insert()
        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()

    def connect_and_read_async(self, results):
        self.connect()
        checker = ConsistencyChecker.ConsistencyChecker()
        checker.run()
        mongoresults = self.load_duplicates_count()
        print('mongoresults')
        print(mongoresults)
        print('tinydb results')
        print(results)
        self.verify_top_ten(mongoresults, results)

    def load_duplicates_count(self):
        results = self.load_all()
        queries = []
        for result in results:
            queries.append(result.get('query').encode("utf-8"))
        something = {}
        something = Counter(queries)
        return something

    def return_topten(self):
        data = self.load_duplicates_count().most_common(10)
        return data

    def verify_top_ten(self, mongoresults, tinydb_results):
        results = mongoresults - tinydb_results
        if (results == Counter()):
            print("We all gucci")
            if mongoresults.most_common(10) == tinydb_results.most_common(10):
                print("Top 10 results the same")
            else: 
                print("Top 10 results NOT the same")
        else:
            print("This no good")
            if mongoresults.most_common(10) == tinydb_results.most_common(10):
                print("Top 10 results the same")
            else: 
                print("Top 10 results NOT the same")
                
            print('\nInconsistencies so far: ' + str(results) + '\n')




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

    def find(self, time):
        return self.db.search(self.User.time == time)


class MongoDatabase(Database):
    def connect(self):
        self.User = MongoClient(
            "mongodb://user123:password123@ds249398.mlab.com:49398/searx").searx
        self.db = self.User.trending

    def load_all(self):
        return self.db.find({})

    def delete(self, query, time):
        return self.db.delete_one({'time':time, 'query':query})

    def delete_all(self):
        self.db.delete_many({})

    def find(self, name):
        return self.db.find_one({'time':name})

    def update_mongo(self, time, old_query, new_query):
        return self.db.find_one_and_update({'time':time, 'query':old_query},
                                                {"$set": {'query': new_query}})
