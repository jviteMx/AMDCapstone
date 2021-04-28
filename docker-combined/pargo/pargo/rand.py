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
