
from pymongo import MongoClient
import pandas as pd

class MongoReader:
    # def __init__():
    #     read_collection(p)
    def get_clientDB(self, host, port, user_name, password, db):
        #get authorized client and connect to DB
        if user_name and password:
            uri = f'mongodb://{user_name}:{password}@{host}:{port}/{db}'
            client = MongoClient(uri)
        else:
            client = MongoClient(host, port)

        return client[db]
    # get DB collection and return pandas dataframe
    def read_collection(self, db, collection, query={}, host='localhost', port=27017, user_name=None, password=None, delete_id=True):
        #read Mongo collection and return pandas DataFrame#
        # Connect to MongoDB
        db = self.get_clientDB(host=host, port=port, user_name=user_name, password=password, db=db)
        cursor = db[collection].find(query)
        
        if db[collection].count_documents({}): #returns falsy value 0 if no document in collection
            df =  pd.DataFrame(list(cursor))

            # Delete default mongo _id 
            if delete_id:
                del df['_id']

            return df
        else:
            return pd.DataFrame()    #empty df. necessary as a df must be returned