# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Creates pymongo client object and read specified collections from specified mongoDB database"""
from urllib.parse import quote_plus
from pymongo import MongoClient
from dotenv import dotenv_values
import pandas as pd

class MongoReader:
    """Creates user defined pymongo client and reads collections from mongoDB"""

    def __init__(self):
        self.dotenv_vals = dotenv_values()
        self.user_name = None
        self.password = None
        self.host = None
        self.db_name = None

    def get_client_db(self, db_name):
        """get authorized client and connect to DB"""
        self.db_name = db_name
        try:
            self.user_name = self.dotenv_vals['PARGO_USER']
            self.password = self.dotenv_vals['PARGO_PASSWORD']
            self.host = self.dotenv_vals['PARGO_HOST']  # ip and port
        except KeyError:
            try:
                self.host = self.dotenv_vals['PARGO_HOST']
            except KeyError:
                pass
        if self.user_name and self.password:
            self.user_name = quote_plus(self.user_name)
            self.password = quote_plus(self.password)

        if self.user_name and self.password and self.host:
            uri = f'mongodb://{self.user_name}:{self.password}@\
                {self.host}/{self.db_name}'
            client = MongoClient(uri)
        elif self.host:
            client = MongoClient(self.host)
        else:
            client = MongoClient()
        return client[self.db_name]

    def read_collection(self, db_name, collection):
        """read Mongo collection and return pandas DataFrame"""
        database = self.get_client_db(db_name)
        query={}
        cursor = database[collection].find(query)
        if database[collection].count_documents({}):
            frame =  pd.DataFrame(list(cursor))
            del frame['_id']
            return frame
        return pd.DataFrame()
