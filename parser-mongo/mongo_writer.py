from pymongo import MongoClient

class DBInserter:
    def __init__(self):
        self.client = MongoClient()             #client = MongoClient('localhost', 27017)
        self.collection_name = ''
    def write_to_db(self, db_name, collection_name, ls_of_dicts):
        db = self.client[db_name]   
        self.collection_name = collection_name
        
        #collection or table
        collection = db[self.collection_name]      

        for i in ls_of_dicts:
            collection.replace_one(i, i, upsert=True)       
        return collection