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

"""Processes all library data and calls db writer interface
to write to mongoDB."""

from pathlib import Path
from statistics import mean, median
from pargo.registry import MongoDBWriter
from pargo.registry import DictionaryModel
from annotate import annotate


class LibrarySuiteProcessor(MongoDBWriter):
    """Library processing base class.

    Processes any rocm math library test suites and hardware specs with the goal of providing
    all data fields required by the structured dictionary in registry module
    for easy write to the database.
    NB:
    The derived class must initialize this base class with address to the database and
    the library name
    NB:
    The process_data method must always be overriden by the derived class.
    In the derived class process data method, the last call should be to the
    base class' write_to_db method.
    """
    # Hint annotations for activate_process method keyword args
    # Most useful for type checkers as it is not enforced at runtime
    StringORNone = annotate.STRING
    PATHListORStringORNone = annotate.DAT_FILE_PATH
    PATHString = annotate.PATH
    List = annotate.STRING_LIST
    Dictionary = annotate.DICT
    STRING_TUPLE = annotate.STRING_TUPLE

    def __init__(self, library_name):
        self.library_name = library_name
        self.data = DictionaryModel()
        self.added_fields = ''
        self.plots = ''
        self.rocm_version = ''
        self.axis_titles = ''
        self.x_axis = ''
        self.y_axis = ''
        self.hardware_id = ''
        self.specs_data = ''
        MongoDBWriter.__init__(self, self.data)

    def activate_process(self, *, platform: StringORNone = None,
                         dat_file_path: PATHListORStringORNone = None,
                         version: StringORNone = None,
                         specs_file_path: PATHString = None,
                         strict_dir_path: PATHString = None,
                         plots: List = None,
                         added_fields: Dictionary = None,
                         axis_titles: List = None,
                         x_axis:STRING_TUPLE = None,
                         y_axis:STRING_TUPLE = None) -> None:

        """After instantiating the base class, this method is called with the
        interested keyword args values. This must be done only after the derived
        class has overriden the process_data method.
        kwargs;
        platform: The hardware id. Should be unique for all NEW hardware.
                  check db to avoid overiding existing db specs data.
                  Preferred format for unque identification
                  is GPU-Server-<No> eg. GPU-Server-1
                  This value should be None when strict_dir_path is not None
                  as it will be infered from the strict path structure.
        dat_file_path: The path to the .dat test suite file. This can be a
                       list of test suite paths for tests run on the same
                       hardware and rocm version. This value should be None
                       when strict_dir_path is not None as it will be infered
                       from the strict path structure.
        version: The rocm version. None for when strict path is used as it will be infered
        specs_file_path: The path to the .txt specs file. None for when strict path is used as
                         it will be infered.
        strict_dir_path: The path to a well structured directory where platform, specs, version,
                         and .dat suite files are specified by how the directory is organized.
                         when not None, all above parameters should be None as their values
                         otherwise would be ignored. Refer to the README for the path structure.
                         Prefered method especially for processing multiple test suites
                         across multiple platforms at a go.
        plots: List of visual plots to be made for this library on dashboard. Plot names
               should be preferably recognized by plotly. eg. lines, lines+markers.
               This arg will be removed in future when dashboard admin is created.
               It can be None for all already implemented libraries. New libraries
               must however supply it.
        added_fields: A dictionary of dashboard field type as key and field value list as values.
                      This dictonary should only be for additional fields. default fields are
                      HardWare_ID, Test_Suite, Version(s), Graph, SpeedUp-Options.
                      It can be None for all already implemented libraries. New libraries.
        axis_titles: list of titles for specified plot axis. Not yet enforced.
        x_axis: Tuple of plottable x_axis columns of table or frame. Not implemented
        y_axis: Tuple of plottable y_axis columns of table or frame. Not implemented
        """
        self.x_axis = x_axis
        self.y_axis =y_axis
        self.added_fields = added_fields
        self.plots = plots
        self.axis_titles = axis_titles
        if strict_dir_path:
            path_object = Path(strict_dir_path)
            platform_dirs = [dir_obj for dir_obj in path_object.iterdir() if dir_obj.is_dir()]
            for platform_path_object in platform_dirs:
                self.retrieve_and_parse_files(platform_path_object)
        if platform and dat_file_path and version and specs_file_path:
            self.rocm_version = version
            self.hardware_id = platform
            self.process_platform_info(Path(specs_file_path), version)
            if isinstance(dat_file_path, list):
                for file_item in dat_file_path:
                    self.process_dat_files(Path(file_item))
            else:
                self.process_dat_files(Path(dat_file_path))

    def retrieve_and_parse_files(self, directory_path_object):
        """If strict directory path option is taken, processes all the
        .dat test suites files in directory sub trees and the
        .txt specs file
        """
        path_obj = directory_path_object
        print('processing', path_obj.name + ' data....')
        spec_txt_path = [obj for obj in path_obj.iterdir() if not obj.is_dir()]
        for obj in path_obj.iterdir():
            if obj.is_dir():
                print(obj.name, 'test suite data')
                self.process_platform_info(spec_txt_path[0], obj.name)
                self.rocm_version = obj.name
                self.hardware_id = obj.parent.name
                self.process_dat_files(obj)

    def process_platform_info(self, file_path_object, rocm_version):
        """Processes the hardware specs data. The lines should be
        exactly 14. The Host heading should be on line 1 and the
        Device heading should be on line 8. Uses with context
        manager for safe open and close of file. Uses open method
        of Pathlib Path object.
        """
        print(file_path_object.parent.name, file_path_object.name)
        host_keys, device_keys, host_values, device_values = [],[],[],[]
        with file_path_object.open() as file:
            data = file.readlines()
            if not (len(data) == 14 and "Host" in data[0] and "Device" in data[7]):
                return
            for i in range(1, 7):
                line = data[i]
                host_keys.append(line.split(':')[0].strip())
                host_values.append(line.split(':')[1].strip())
            for i in range(8, 14):
                line = data[i]
                device_keys.append(line.split(':')[0].strip())
                device_values.append(line.split(':')[1].strip())
        host_values[5] = rocm_version
        host_data = dict(zip(host_keys, host_values))
        device_data = dict(zip(device_keys, device_values))
        spec_data = [{'Host info': host_data}, {'Device info': device_data}]
        self.specs_data = spec_data

    def process_dat_files(self, path_object):
        """Satisfies any activation option used."""
        if path_object.is_dir():
            for dat_file_path_obj in path_object.glob('*.dat'):
                self.open_and_process_data(dat_file_path_obj)
        else:
            self.open_and_process_data(path_object)

    def open_and_process_data(self, file_path_object):
        """Open with Pathlib Path object open method.
        Uses with context manager for safe open and close.
        Read file and pass data to the overriden
        process_data method in derived class.
        """
        with file_path_object.open() as file:
            data = file.readlines()
            self.process_data(data, file_path_object)

    def process_data(self, list_data, file_path_object):
        """This method should be overriden in all derived classes.
        The method MUST call write_to_db and the call should be the last call
        in the method as far as parsing and writing data to the db is concerned.
        args;
        list_data: list of all lines read from test suites using the opened file readlines method.
        file_path_object: Pathlib Path object for the file that has been read with readlines.
        """

    def write_to_db(self, suite_name, suite_data):
        """This method makes the fields data for the test suite dictonary object and calls
        the writer to write this suite data to the db.
        args;
        suite_name: the processed name of the test suite. This should be as expected on the
                    dashboard so best possible unique names should be passed.
        suite_data: list of dictionaries containing the data to write to the db.
                    think of it as the documents for the test suite collection.
        """
        self.data.make_fields(hardware_id=self.hardware_id, specs_ls_of_dict=self.specs_data,
                             library_name=self.library_name, rocm_version=self.rocm_version,
                             suite_name=suite_name, suite_data=suite_data,
                             added_fields=self.added_fields,
                             plots=self.plots, axis_titles=self.axis_titles, x_axis=self.x_axis, y_axis=self.y_axis)
        self.run_writer()


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

    @staticmethod
    def fulfil_dimensionwise_values(list_data, iter_number, keys_list):
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

    @staticmethod
    def append_statistics(values:list, sample_values:list) -> list:
        """Add stats of average and mean of the sample runs to
        the list of values
        args;
        values: list of values
        """
        the_mean = mean(list(map(float, sample_values)))
        the_median = median(list(map(float, sample_values)))
        values.extend((the_mean, the_median))
        return values

    @staticmethod
    def process_file_name(file_path_object):
        """Process file name as test suite name preferred on dashboard"""
        name_parts = file_path_object.name.split('_')
        const_part_1 = name_parts[:4]
        const_part_2 = name_parts[-1]
        rename_part1 = const_part_1[0][0] + const_part_1[0][-1] + '-' + const_part_1[1][0] +\
             const_part_1[1][-1] + '-'
        rename_part2 = '-'.join(name_parts[4:-1])
        rename_part3 = '-' + const_part_2[0] + 'p'
        renamed = rename_part1 + rename_part2 + rename_part3
        return renamed.lower()


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

    @staticmethod
    def process_file_name(file_path_object):
        """Process file name as test suite name preferred on dashboard"""
        renamed = file_path_object.name.rstrip('recision.dat').lower()
        return renamed


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

    @staticmethod
    def process_suite_name(info, file_path_object):
        """Process file name as test suite name preferred on dashboard"""
        renamed = info.split(':')
        renamed = [i.strip() for i in renamed]
        renamed = '-'.join(renamed)
        renamed = renamed.replace(' ', '')
        renamed = file_path_object.name.split('.dat')[0] + renamed
        return renamed.lower()
