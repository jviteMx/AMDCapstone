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

"""Creates MongoDB client and writes data to mongo."""


from urllib.parse import quote_plus
from pymongo import MongoClient
from dotenv import dotenv_values


class PymongoWriter:
    """The MongoDB writer instance class.

    provides interface for writing all data to the DB.
    """

    def __init__(self, db_client):
        """Client should be provided at initialization."""
        self.db_client = db_client
        self.db = ''

    def write_data_to_mongo(self, db_name, collection_name, list_of_dicts):
        """Write any list of dictionary data to the database."""
        self.db_client.db_name = db_name
        self.db = self.db_client.affirm_client()
        collection = self.__write(collection_name, list_of_dicts)
        return collection

    def __write(self, collection_name, ls_of_dicts):
        collection = self.db[collection_name]
        for i in ls_of_dicts:
            collection.replace_one(i, i, upsert=True)
        return collection


class PymongoClient:
    """The MongoDB pymongo client class.

    host should be both ip and port.
    """

    def __init__(self):
        """Information needed to to create client."""
        dotenv_vals = dotenv_values()
        if dotenv_vals.__len__() == 0:
            print('You have not provided a .env file with address to database'
                  '. Program will attempt to use address it finds during execution')
        self.user_name = ''
        self.password = ''
        self.host = ''
        try:
            self.user_name = dotenv_vals['PARGO_USER']
            self.password = dotenv_vals['PARGO_PASSWORD']
            self.host = dotenv_vals['PARGO_HOST']  # ip and port
        except KeyError:
            try:
                self.host = dotenv_vals['PARGO_HOST']
                print('You provided only host info to database in .env'
                      ' .Program will attempt to use address.')
            except KeyError:
                pass
        if self.user_name and self.password:
            self.user_name = quote_plus(self.user_name)
            self.password = quote_plus(self.password)
        self.db_name = None   # would not be none during affirm_client call

    def affirm_client(self):
        """Dynamic client. Returns pymongo client object."""
        if self.user_name and self.password and self.host:
            uri = f'mongodb://{self.user_name}:{self.password}@\
                {self.host}/{self.db_name}'
            client = MongoClient(uri)
        elif self.host:
            client = MongoClient(self.host)
        else:
            client = MongoClient()
        return client[self.db_name]
