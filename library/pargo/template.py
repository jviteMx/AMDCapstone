# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Processes all library data and calls db writer interface
to write to mongoDB."""

from pathlib import Path
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

    def __init__(self, library_name):
        self.library_name = library_name
        self.data = DictionaryModel()
        self.added_fields = ''
        self.plots = ''
        self.rocm_version = ''
        self.axis_titles = ''
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
                         axis_titles: List = None) -> None:
        """After instantiating the base class, this method is called with the
        interested keyword args. This must be done only after the derived
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
                         when not None, all these parameters should be None as their values
                         otherwise would be ignored. Refer to the README for the path structure.
                         Prefered method especially for processing multiple test suites
                         across multiple platforms at a go.
        plots: List of visual plots to be made for this library on dashboard. Plot names
               should be preferably recognized by plotly. eg. lines, lines+markers.
               This arg will be removed in future when dashboard admin is created.
               It can be None now as it is not enforced yet.
        added_fields: A dictionary of dashboard field type as key and field value list as values.
                      This dictonary should only be for additional fields. default fields are
                      HardWare_ID, Test_Suite, Version(s), Graph, SpeedUp-Options
                      see example in rand module.
        axis_titles: list of titles for specified plot axis. Not yet enforced.
        """
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
        sub_dirs = [obj for obj in path_obj.iterdir()]
        spec_txt_path = [obj for obj in sub_dirs if not obj.is_dir()]
        for obj in sub_dirs:
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
                             plots=self.plots, axis_titles=self.axis_titles)
        self.run_writer()
