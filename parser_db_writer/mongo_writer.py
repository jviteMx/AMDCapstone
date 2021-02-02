from pymongo import MongoClient

class DBInserter:
    def __init__(self):
        self.client = MongoClient()             #client = MongoClient('localhost', 27017)

    def write_to_db(self, ls_of_dicts):
        db = self.client.AMD_DATA    #OR db = self.client['AMD_DATA'] 
        #Drop collections to avoid repeating documents/entries when re-run
        db.example_collection.drop()
        
        #collection or table
        example_collection = db.example_collection                #example_collection collection
        example_collection.insert_many(ls_of_dicts)               #insert full file data to db

        return example_collection