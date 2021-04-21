# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Processes rocblas library data by customizing the base LibrarySuiteProcessor by overriding
the process_data method and calling db writer interface to write to mongoDB"""

from pargo.template import LibrarySuiteProcessor


class BLASSuiteProcessor(LibrarySuiteProcessor):
    """rocBLAS suite processor.

    Initializes the base processor with the library name and mongo db address and
    focuses on processing the .dat suite data (passed to the process_data
    method as a list of lines of the file and Pathlib Path object of the file) and
    suite name customizing.
    """

    LIBRARY_NAME = 'rocBLAS'
    def __init__(self):
        self.suite_name = ''
        self.suite_data = ''
        LibrarySuiteProcessor.__init__(self, library_name=BLASSuiteProcessor.LIBRARY_NAME)

    def process_data(self, list_data, file_path_object):
        data = list_data
        list_of_dicts = []
        keys = data[0].strip('#').strip().split(',')
        for i in range(1, len(data)):
            values = data[i].split()
            dict_data = dict(zip(keys, values))
            list_of_dicts.append(dict_data)
        file_name = self.process_file_name(file_path_object)
        self.suite_name = file_name
        self.suite_data = list_of_dicts

        self.write_to_db(self.suite_name, self.suite_data)

    def process_file_name(self, file_path_object):
        """Process file name as test suite name preferred on dashboard"""
        renamed = file_path_object.name.rstrip('recision.dat').lower()
        return renamed
