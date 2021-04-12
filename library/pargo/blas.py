# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Processes rocblas library data by customizing the base LibraryProcessor by overriding
the process_data method and calling db writer interface to write to mongoDB"""

from pargo.template import LibraryProcessor
class BLASProcessor(LibraryProcessor):
    """rocBLAS suite processor.

    Initializes the base processor with the library name and mongo db address and
    focuses on processing the .dat suite data (passed to the process_data
    method as a list of lines of the file and Pathlib Path object of the file) and
    suite name customizing.
    """
    def __init__(self):
        self.library_name = 'rocBLAS'
        self.CLIENT_IP = 'localhost'
        self.CLIENT_PORT = 27017
        self.suite_data = ''
        self.suite_name = ''
        LibraryProcessor.__init__(self, self.CLIENT_IP, self.CLIENT_PORT, self.library_name)

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
#Uncomment the below for use as script with strict dir path
# if __name__ == '__main__':
#     blas = BLASProcessor()
#     blas.activate_process(strict_dir_path='assets')
