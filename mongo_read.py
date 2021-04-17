# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Creates pymongo client object and read specified collections from specified mongoDB database"""
from pymongo import MongoClient
import pandas as pd

class MongoReader:
    """Creates user defined pymongo client and reads collections from mongoDB"""
    def get_client_db(self, host, port, user_name, password, database):
        """get authorized client and connect to DB"""
        if user_name and password:
            uri = f'mongodb://{user_name}:{password}@{host}:{port}/{database}'
            client = MongoClient(uri)
        else:
            client = MongoClient(host, port)

        return client[database]

    def read_collection(self, database, collection, host='localhost', port=27017,
                       user_name=None, password=None):
        """read Mongo collection and return pandas DataFrame"""
        # Connect to MongoDB
        database = self.get_client_db(host=host, port=port, user_name=user_name,
                                     password=password, database=database)
        query={}
        cursor = database[collection].find(query)
        if database[collection].count_documents({}):
            frame =  pd.DataFrame(list(cursor))
            del frame['_id']
            return frame
        return pd.DataFrame()
