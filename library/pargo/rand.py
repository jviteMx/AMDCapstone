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
class RANDSuiteProcessor(LibrarySuiteProcessor):
    """rocRAND suite processor.

    Initializes the base processor with the library name and mongo db address and
    focuses on processing the .dat suite data (passed to the process_data
    method as a list of lines of the file and Pathlib Path object of the file) and
    suite name customizing.
    """

    LIBRARY_NAME = 'rocRAND'
    def __init__(self):
        self.suite_name = ''
        self.suite_data = ''
        LibrarySuiteProcessor.__init__(self, library_name=RANDSuiteProcessor.LIBRARY_NAME)

    def process_data(self, list_data, file_path_object):
        data = list_data
        file_name = data[0]
        self.suite_name = self.process_suite_name(file_name, file_path_object)
        grouped_data = [('xorwow', data[2:25]),('mrg32k3a', data[26:49]),('mtgp32', data[50:73]),
                        ('philox', data[74:97]),('sobol32', data[98:121])]
        ls_of_dicts = []                
        for algo_data in grouped_data:
            ALGO = algo_data[0]
            data = algo_data[1]
            sub_data = data[1:]
            for _, line_data in enumerate(sub_data):
                if 'Throughput' not in line_data:
                    ALGO = ALGO + '@' + line_data.strip().strip(':').replace(' ', '')
                    continue
                keys = ['Algorithm', 'Throughput-GB/s', 'Samples-GSample/s',
                        'AvgTime(1 trial)-ms', 'Time(all)-ms', 'Size']
                values = []
                process_a = [item.strip() for item in line_data.split(',')]
                process_b = [item.split('=') for item in process_a]
                process_c = [[i.strip(), j.strip()] for [i, j] in process_b]
                temp = process_c[-1]
                process_d = [[i.strip(' ') + '-' + j.split(' ')[1], j.split(' ')[0]]
                                for [i, j] in process_c[:-1]]
                process_d.append(temp)
                process_e = [i[1] for i in process_d]
                values.append(ALGO)
                values = values + process_e
                dict_data = dict(zip(keys, values))
                ls_of_dicts.append(dict_data)
                ALGO = algo_data[0]         
        self.suite_data = ls_of_dicts
        self.write_to_db(self.suite_name, self.suite_data)

    def process_suite_name(self, info, file_path_object):
        """Process file name as test suite name preferred on dashboard"""
        renamed = info.split(':')
        renamed = [i.strip() for i in renamed]
        renamed = '-'.join(renamed)
        renamed = renamed.replace(' ', '')
        renamed = file_path_object.name.split('.dat')[0] + renamed
        return renamed.lower()
