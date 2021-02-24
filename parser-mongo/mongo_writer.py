from pymongo import MongoClient

class DBInserter:
    def __init__(self):
        self.client = MongoClient()             #client = MongoClient('localhost', 27017)

    def write_to_db(self, db_name, collection_name, ls_of_dicts):
        db = self.client[db_name]   #OR db = self.client['AMD_DATA'] 
        self.collection_name = collection_name
        
        #collection or table
        collection = db[self.collection_name]               # collection
        # if len(ls_of_dicts) > 1:
        #     for i in ls_of_dicts:
        #         collection.replace_one(i, i, upsert=True)                 #insert full file data to db  
        # else:
        #     collection.replace_one(ls_of_dicts[0], ls_of_dicts[0], upsert=True)  

        for i in ls_of_dicts:
            collection.replace_one(i, i, upsert=True)       
        return collection