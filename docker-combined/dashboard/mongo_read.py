# MIT License

# This project is a software package to automate the performance tracking of the HPC algorithms

# Copyright (c) 2021. Victor Tuah Kumi, Ahmed Iqbal, Javier Vite, Aidan Forester

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
            client = MongoClient('mongodb://rocm_mongo:27017')
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
