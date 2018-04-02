from __future__ import print_function
import DatabaseHandler as db
import json
from concurrent import futures

class consistencyChecker():

    def __init__(self):
        self.inconsistencies = 0;
        self.inconsistency_messages = []
        self.rows_tiny_checked = []
        self.row_mongo_checked = []

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
        for row_in_tinydb in tinytable:
            time = row_in_tinydb['time']
            mongoQuery = mongodb.find(time)

            # if row does not exist in mongodb then insert it
            if(not mongoQuery):
                inconsistency_message = "inconsistency found : missing row in mongodb " + row_in_tinydb['time'] + "-" + row_in_tinydb['query']
                self.inconsistency_messages.append(inconsistency_message)
                self.inconsistencies += 1
                mongodb.prepare_data(row_in_tinydb)
                mongodb.insert()

            # row exists but inconsistent
            elif(mongoQuery and mongoQuery['query'] != row_in_tinydb['query']):
                self.row_mongo_checked.append(mongoQuery)
                inconsistency_message = "inconsistency found at ' + row_in_tinydb['time'] + '. \n Expected: ' + row_in_tinydb['query'] + '\nReceived: ' + mongoQuery"
                print(inconsistency_message)
                self.inconsistency_messages.append(inconsistency_message)
                self.inconsistencies += 1
                print('\nInconsistencies so far: ' + self.inconsistencies + '\n')

                #update the worng entry from MongoDB with the old entry from Tinydb
                mongodb.update_mongo(row_in_tinydb['time'], mongoQuery['query'], row_in_tinydb['query'])

            self.rows_tiny_checked.append(row_in_tinydb)


if __name__ == '__main__':
    classes = []
    with futures.ThreadPoolExecutor(max_workers = 1) as executor:
        #need to pass something in submit(), not sure what
        futures_classes = {executor.submit()}
    consistencyChecker().run()
