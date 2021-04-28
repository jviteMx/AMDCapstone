# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Creates Intermediary dictionary object that contains
the data to be written to the database. Also implements
the methods for writing the dictionary data to the database.
"""

from pargo.mongowrite import PymongoClient
from pargo.mongowrite import PymongoWriter


class DictionaryModel(dict):
    """Dictionary class"""
    def make_fields(self, *, hardware_id, specs_ls_of_dict,
                    library_name, rocm_version, suite_name,
                    added_fields=None, suite_data, plots=None,
                    axis_titles=None, x_axis=None, y_axis=None):
        """Makes the dictionary object data fields. Unimplemented x and y axis."""
        _ = x_axis
        __= y_axis
        self['hardware_id'] = hardware_id
        self['specs_data'] = specs_ls_of_dict
        self['library_name'] = library_name
        self['rocm_version'] = rocm_version
        self['suite_name'] = suite_name
        self['field_types'] = ['HardWare-ID','Test-Suite', 'Version(s)', 'Graph', 'SpeedUp-Options']
        if added_fields:
            added_field_types = list(added_fields.keys())
            self['field_types'] = self['field_types'] + added_field_types
            self['added_field_values'] = list(added_fields.values())
        self['suite_data'] = suite_data
        self['plots'] = plots
        self['axis_titles'] = axis_titles
        if self['library_name'].lower() == 'rocfft' or self['library_name'].lower() == 'rocblas':
            self['field_types'] =['HardWare-ID', 'Test-Suite', 'Version(s)', 'Graph', 'SpeedUp-Options']
            self['plots'] = ['line', 'line+marker']
        if self['library_name'].lower() == 'rocfft':
            self['axis_titles'] = ['xlength', 'median']
        if  self['library_name'].lower() == 'rocblas':
            self['axis_titles'] = ['rocblas-Gflops', 'us']
        if  self['library_name'].lower() == 'rocrand':
            self['axis_titles'] = ['uniform-unit', 'uniform-float', 'uniform-double', 'normal-float',
                'normal-double', 'log-normal-float','log-normal-double', 'poisson lambda 10.0',
                'discrete-poisson lambda 10.0', 'discrete-custom']
            self['field_types'] =  ['HardWare-ID','Test-Suite', 'Version(s)', 'Graph', 'SpeedUp-Options', 'Algorithm']
            self['added_field_values'] = [['xorwow', 'mrg32k3a', 'mtgp32', 'philox', 'sobol32']]
            self['plots'] = ['bar']

class MongoDBWriter(PymongoWriter):
    """Implements methods for writing data to the db and registering names to
     be used on dashboard"""
    def __init__(self, dictobj):
        self.data = dictobj
        self.inserter = PymongoClient()
        self.suite_collection_name = ''
        self.aux_db = ''
        PymongoWriter.__init__(self, self.inserter)

    def run_writer(self):
        """Creates the collection name for the suite data and the auxiliary db that hosts
        the auxiliary data mainly used for the dashboard. Calls the public method that
        writes all data to the database."""
        self.suite_collection_name = self.data['hardware_id'].lower() + '/' + \
            self.data['library_name'].lower() + '/' + self.data['rocm_version'].lower() + \
            '/'  + self.data['suite_name'].lower()

        self.aux_db = 'aux-db'
        self.register_data()

    def __write_data_to_mongo(self):
        self.write_data_to_mongo(self.data['hardware_id'].lower(),
                                self.suite_collection_name, self.data['suite_data'])

    def __register_suite_name(self):
        collection_name = self.data['library_name'].lower() + 'test-suitefieldvalue'
        ls_of_dicts = [{'name': self.data['suite_name']}]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

    def __register_hardware_id(self):
        collection_name = self.data['library_name'].lower() + 'hardware-idfieldvalue'
        ls_of_dicts = [{'name': self.data['hardware_id']}]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

    def __register_rocm_version(self):
        collection_name = self.data['library_name'].lower() + 'version(s)fieldvalue'
        ls_of_dicts = [{'name': self.data['rocm_version']}]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

    def __register_plots(self):
        collection_name = self.data['library_name'].lower() + 'graphfieldvalue'
        ls_of_dicts = [{'name': plot} for plot in self.data['plots']]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

    def __register_library(self):
        collection_name = 'libraries'
        ls_of_dicts = [{'name': self.data['library_name']}]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

    def __register_dash_field_types(self):
        collection_name = self.data['library_name'].lower() + 'field_type'
        ls_of_dicts = [{'name': field_type} for field_type in self.data['field_types'] if
                self.data['field_types'] is not None and isinstance(self.data['field_types'], list)]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

    def __register_axis_titles(self):
        if self.data['axis_titles'] is not None:
            collection_name = self.data['library_name'].lower() + 'plot_axis'
            ls_of_dicts = [{'name': title} for title in self.data['axis_titles']]
            self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)
        else:
            pass

    def __register_field_values(self):
        if len(self.data['field_types']) > 5:
            for i in range(len(self.data['field_types'][5:])):
                collection_name = self.data['library_name'].lower() + \
                    self.data['field_types'][5:][i].lower() + 'fieldvalue'
                ls_of_dicts = [{'name': field_value} for field_value in
                              self.data['added_field_values'][i]]
                self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)
        else:
            pass

    def __write_specs_to_mongo(self):
        collection_name = self.data['hardware_id'].lower() + '/' + \
                    self.data['library_name'].lower() + '/' + self.data['rocm_version'].lower() + \
                    '/' + self.data['suite_name'].lower() + 'hostspecs'
        ls_of_dicts = [self.data['specs_data'][0]['Host info']]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

        collection_name = self.data['hardware_id'].lower() + '/' + \
            self.data['library_name'].lower() + '/' + self.data['rocm_version'].lower() + \
            '/' + self.data['suite_name'].lower() + 'devicespecs'
        ls_of_dicts = [self.data['specs_data'][1]['Device info']]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

    def __write_gpu_rocm_specs(self):
        """Redundant method collection to be used when db is collapsed to only one."""
        collection_name = self.data['hardware_id'].lower() + '/' + \
            self.data['rocm_version'] + '/' + 'hostspecs'
        ls_of_dicts = [self.data['specs_data'][0]['Host info']]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)

        collection_name = self.data['hardware_id'].lower() + '/' + \
            self.data['rocm_version'] + '/' + 'devicespecs'
        ls_of_dicts = [self.data['specs_data'][1]['Device info']]
        self.write_data_to_mongo(self.aux_db, collection_name, ls_of_dicts)


    def register_data(self):
        """Calls the private db data registration
        methods.
        """
        self.__register_dash_field_types()
        self.__register_field_values()
        self.__register_hardware_id()
        self.__register_library()
        self.__register_axis_titles()
        self.__register_suite_name()
        self.__register_rocm_version()
        self.__register_plots()
        self.__write_specs_to_mongo()
        self.__write_gpu_rocm_specs()
        self.__write_data_to_mongo()
