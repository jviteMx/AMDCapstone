from template import LibraryProcessor
class BLASProcessor(LibraryProcessor):
    def __init__(self):
        self.library_name = 'rocBLAS'
        self.CLIENT_IP = 'localhost'
        self.CLIENT_PORT = 27017
        LibraryProcessor.__init__(self, self.CLIENT_IP, self.CLIENT_PORT, self.library_name)

    def process_data(self, list_data, file_path_object):
        data = list_data
        list_of_dicts = []
        keys = data[0].strip('#').split()
        for i in range(1, len(data)):
            values = data[i].split()
            dict_data = dict(zip(keys, values))
            list_of_dicts.append(dict_data)
        file_name = self.process_file_name(file_path_object)
        self.suite_name = file_name
        self.suite_data = list_of_dicts

        self.run(self.suite_name, self.suite_data)

    def process_file_name(self, file_path_object): 
        renamed = file_path_object.name.rstrip('recision.dat').lower()
        return renamed 

blas = BLASProcessor()
blas.activate_process(strict_dir_path='assets')