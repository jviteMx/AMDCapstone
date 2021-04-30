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

"""Processes rocfft library data by customizing the base LibrarySuiteProcessor by overriding
the process_data method and calling db writer interface to write to mongoDB"""

from statistics import mean, median
from pargo.template import LibrarySuiteProcessor
class FFTSuiteProcessor(LibrarySuiteProcessor):
    """rocFFT suite processor.

    Initializes the base processor with the library name and mongo db address and
    focuses on processing the .dat suite data (passed to the process_data
    method as a list from readlines() of the file, and Pathlib Path object of the file) and
    suite name customizing.
    """

    LIBRARY_NAME = 'rocFFT'
    def __init__(self):
        self.suite_name = ''
        self.suite_data = ''
        LibrarySuiteProcessor.__init__(self, library_name=FFTSuiteProcessor.LIBRARY_NAME)

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
if __name__ == '__main__':
    fft = FFTSuiteProcessor()
    fft.activate_process(strict_dir_path='assets')
