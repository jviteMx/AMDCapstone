# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Creates MongoDB client and writes data to mongo"""

from pymongo import MongoClient

class MongoWriter:
    """The MongoDB writer instance class.

    provides interface for writing all data to the DB.
    """
    def __init__(self, inserter_obj):
        self.writer = inserter_obj

    def write_data_to_mongo(self, database, collection_name, list_of_dicts):
        """Writes any list of dictionary data to the database"""
        self.writer.write_to_db(database, collection_name, list_of_dicts)


class ClientWriter:
    """The MongoDB pymongo client class.

    Creates the pymongo client and writes to the db, the list of dicts
    data transferred from the writer object.
    """
    def __init__(self, client_ip, client_port):
        self.client = MongoClient(client_ip, client_port)
        self.collection_name = ''
    def write_to_db(self, db_name, collection_name, ls_of_dicts):
        """Writes any list of dictionary data to the database"""
        db = self.client[db_name]
        self.collection_name = collection_name

        #collection or table
        collection = db[self.collection_name]

        for i in ls_of_dicts:
            collection.replace_one(i, i, upsert=True)
        return collection
