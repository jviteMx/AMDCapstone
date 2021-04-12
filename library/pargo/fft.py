# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Processes rocfft library data by customizing the base LibraryProcessor by overriding
the process_data method and calling db writer interface to write to mongoDB"""

from statistics import mean, median
from pargo.template import LibraryProcessor
class FFTProcessor(LibraryProcessor):
    """rocFFT suite processor.

    Initializes the base processor with the library name and mongo db address and
    focuses on processing the .dat suite data (passed to the process_data
    method as a list of lines of the file and Pathlib Path object of the file) and
    suite name customizing.
    """
    def __init__(self):
        self.library_name = 'rocFFT'
        self.CLIENT_IP = 'localhost'
        self.CLIENT_PORT = 27017
        self.suite_name = ''
        self.suite_data = ''
        LibraryProcessor.__init__(self, self.CLIENT_IP, self.CLIENT_PORT, self.library_name)

    def process_data(self, list_data, file_path_object):
        data = list_data
        del data[0]
        list_of_dicts = []
        keys = data[0].split()[1:]
        del keys[-1]
        keys.extend(('mean', 'median')) 
        for i in range(1, len(data)):
            values, sample_values = self.fulfil_dimensionwise_values(data, i, keys)
            values_extended = self.append_statistics(values, sample_values)
            dict_data = dict(zip(keys, values_extended))
            list_of_dicts.append(dict_data)
        file_name = self.process_file_name(file_path_object)
        self.suite_name = file_name
        self.suite_data = list_of_dicts

        self.write_to_db(self.suite_name, self.suite_data)

    def fulfil_dimensionwise_values(self, list_data, iter_number, keys_list):
        """Ensure all dimensions are captured correctly"""
        data = list_data
        i = iter_number
        values = data[i].split()[0:4] 
        sample_values = data[i].split()[4:]
        if ('xlength' in keys_list) and ('ylength' in keys_list) and ('zlength' in keys_list):
            values = data[i].split()[0:6] 
            sample_values = data[i].split()[6:]
        elif ('xlength' in keys_list) and ('ylength' in keys_list):
            values = data[i].split()[0:5] 
            sample_values = data[i].split()[5:]
        else:
            pass
        values.append(sample_values)
        return values, sample_values

    def append_statistics(self, values:list, sample_values:list) -> list:
        """Add stats of average and mean of the sample runs to
        the list of values
        args;
        values: list of values
        """
        the_mean = mean(list(map(float, sample_values)))
        the_median = median(list(map(float, sample_values)))
        values.extend((the_mean, the_median))
        return values

    def process_file_name(self, file_path_object):
        """Process file name as test suite name preferred on dashboard"""
        name_parts = file_path_object.name.split('_')
        CONST_PART1 = name_parts[:4]
        CONST_PART2 = name_parts[-1]
        rename_part1 = CONST_PART1[0][0] + CONST_PART1[0][-1] + '-' + CONST_PART1[1][0] +\
             CONST_PART1[1][-1] + '-'
        rename_part2 = '-'.join(name_parts[4:-1])
        rename_part3 = '-' + CONST_PART2[0] + 'p'
        renamed = rename_part1 + rename_part2 + rename_part3
        return renamed.lower()
#Uncomment the below for use as script with strict dir path
# if __name__ == '__main__':
#     fft = FFTProcessor()
#     fft.activate_process(strict_dir_path='assets')
