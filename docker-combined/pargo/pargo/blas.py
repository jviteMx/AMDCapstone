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
