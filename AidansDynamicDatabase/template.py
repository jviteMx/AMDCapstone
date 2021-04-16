import argparse
import sys
from pathlib import Path
# import send2trash
from statistics import mean, median
from writermodel import DBWriter, ModelDictionary

class LibraryProcessor(DBWriter):
    def __init__(self, client_ip, client_port, library_name):
        self.library_name = library_name
        self.data = ModelDictionary()
        DBWriter.__init__(self, self.data, client_ip, client_port)
    def activate_process(self, *, platform=None, dat_file=None, version=None, specs_file=None, strict_dir_path=None, 
                         plots=None, added_fields=None, axis_titles=None):
        self.added_fields = added_fields
        self.plots = plots
        self.axis_titles = axis_titles                 
        if strict_dir_path:
            path_object = Path(strict_dir_path)
            platform_dirs = [dir_obj for dir_obj in path_object.iterdir() if dir_obj.is_dir()]
            for platform_path_object in platform_dirs:
                self.retrieve_and_parse_files(platform_path_object) 
        if platform and dat_file and version and specs_file:
            self.rocm_version = version
            self.hardware_id = platform
            self.process_platform_info(Path(specs_file), version)
            if isinstance(dat_file, list):
                for file_item in dat_file:
                    self.process_dat_files(Path(file_item))
            else:
                self.process_dat_files(Path(dat_file))   

    def retrieve_and_parse_files(self, directory_path_object):
        path_obj = directory_path_object
        print('processing', path_obj.name + ' data....')
        sub_dirs = [obj for obj in path_obj.iterdir()]
        spec_txt_path = [obj for obj in sub_dirs if not obj.is_dir()]
        for obj in sub_dirs:
            if obj.is_dir():
                self.process_platform_info(spec_txt_path[0], obj.name) 
                print(obj.name, spec_txt_path[0].name)
                self.rocm_version = obj.name
                self.hardware_id = obj.parent.name
                self.process_dat_files(obj)
                      
    def process_platform_info(self, file_path_object, rocm_version):
        host_keys, device_keys, host_values, device_values = [],[],[],[]
        with file_path_object.open() as f:
            data = f.readlines()
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
        if path_object.is_dir():
            for datFilePathObj in path_object.glob('*.dat'):
                self.open_and_process_data(datFilePathObj)
        else:
            self.open_and_process_data(path_object)     

    def open_and_process_data(self, file_path_object):
        with file_path_object.open() as f:
            data = f.readlines()
            self.process_data(data, file_path_object)
            #send2trash.send2trash(file_path_object)   

    def process_data(self, list_data, file_path_object):
        pass   

    

    def run(self, suite_name, suite_data):
        self.data.make_fields(hardware_id=self.hardware_id, specs_ls_of_dict=self.specs_data, library_name=self.library_name, rocm_version=self.rocm_version,
                    suite_name=suite_name, suite_data=suite_data, added_fields=self.added_fields, plots=self.plots, axis_titles=self.axis_titles)
        self.run_writer()                                                                