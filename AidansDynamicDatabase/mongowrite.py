from pymongo import MongoClient

class MongoWriter:
    def __init__(self, inserter_obj):
        self.writer = inserter_obj

    def write_data_to_mongo(self, db, collection_name, list_of_dicts):
        self.writer.write_to_db(db, collection_name, list_of_dicts)   


class DBInserter:
    def __init__(self, client_ip, client_port):
        self.client = MongoClient(client_ip, client_port)             #client = MongoClient('localhost', 27017

    def write_to_db(self, db_name, collection_name, ls_of_dicts):
        db = self.client[db_name]   
        self.collection_name = collection_name
        
        #collection or table
        collection = db[self.collection_name]      

        for i in ls_of_dicts:
            collection.replace_one(i, i, upsert=True)       
        return collection