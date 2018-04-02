import DatabaseHandler as db
from datetime import datetime
import requests
import json

class ConsistencyChecker():

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

                r = requests.post("http://funapp.pythonanywhere.com/report", data=json.dumps({
                    "type": "Missing row inconsistencies",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": inconsistency_message}),
                                  headers={'Content-Type': 'application/json'})

                self.inconsistencies += 1
                mongodb.prepare_data(row_in_tinydb)
                mongodb.insert()

            # row exists but inconsistent
            elif(mongoQuery and mongoQuery['query'] != row_in_tinydb['query']):
                self.row_mongo_checked.append(mongoQuery)
                inconsistency_message = "inconsistency found at " + row_in_tinydb['time'] + " Expected: " + row_in_tinydb['query'] + " Received: " + str(mongoQuery)
                print(inconsistency_message)

                r = requests.post("http://funapp.pythonanywhere.com/report", data=json.dumps({
                    "type": "Write inconsistencies",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": inconsistency_message}),
                                  headers={'Content-Type': 'application/json'})

                self.inconsistency_messages.append(inconsistency_message)
                self.inconsistencies += 1
                print('\nInconsistencies so far: ' + str(self.inconsistencies) + '\n')

                #update the worng entry from MongoDB with the old entry from Tinydb
                mongodb.update_mongo(row_in_tinydb['time'], mongoQuery['query'], row_in_tinydb['query'])

            self.rows_tiny_checked.append(row_in_tinydb)

        # relead all data. row exists in mongo but not in tinydb : delete it in mongo
        mongotable = mongodb.load_all()
        for row_in_mongodb in mongotable:
            time = row_in_mongodb['time']
            tinydb_query = tinydb.find(time)

            if(not tinydb_query):
                inconsistency_message = "inconsistency found : extra row in mongodb " + row_in_mongodb['time'] + "-" + row_in_mongodb['query']
                self.inconsistency_messages.append(inconsistency_message)

                r = requests.post("http://funapp.pythonanywhere.com/report", data=json.dumps({
                    "type": "Missing row inconsistencies",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": inconsistency_message}),
                                  headers={'Content-Type': 'application/json'})

                self.inconsistencies += 1
                mongodb.delete(row_in_mongodb['query'], row_in_mongodb['time'])


        # generating report
        r = requests.post("http://funapp.pythonanywhere.com/consistency", data=json.dumps({
                            "inconsistencies":self.inconsistencies,
                            "total_number":len(self.rows_tiny_checked),
                            "date":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}), headers={'Content-Type':'application/json'})
        self.output = r.content
