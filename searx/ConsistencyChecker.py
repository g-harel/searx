from __future__ import print_function
import DatabaseHandler as db
import json
from concurrent import futures

class consistencyChecker():
    inconsistencies = 0

    def run(self):
        #Tinydb connection:
        tinydb = db.TinyDatabase()
        tinydb.connect()
        tinytable = tinydb.load_all()
        print (tinytable)

        #MongoDB connection:
        mongodb = db.MongoDatabase()
        mongodb.connect()
        mongotable = mongodb.load_all()
        print (mongotable)

        #going through rows and checking consistency based on the time of the query:
        for row in tinytable:
            time = row['time']
            mongoQuery = mongodb.find(time)
            if(mongoQuery != row['query']):
                print('inconsistency found at ' + row['time'] + '. \n Expected: ' + row['query'] + '\nReceived: ' + mongoQuery)
                inconsistencies += 1
                print('\nInconsistencies so far: ' + inconsistencies + '\n')
                #update the worng entry from MongoDB with the old entry from Tinydb
                db.update_mongo(row['time'],row['query'])




if __name__ == '__main__':
    classes = []
    with futures.ThreadPoolExecutor(max_workers = 1) as executor:
        #need to pass something in submit(), not sure what
        futures_classes = {executor.submit()}
    consistencyChecker().run()
