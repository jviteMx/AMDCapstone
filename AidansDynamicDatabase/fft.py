from statistics import mean, median
from template import LibraryProcessor
class FFTProcessor(LibraryProcessor):
    def __init__(self):
        self.library_name = 'rocFFT'
        self.CLIENT_IP = 'localhost'
        self.CLIENT_PORT = 27017
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

        self.run(self.suite_name, self.suite_data)

    def fulfil_dimensionwise_values(self, list_data, iter_number, keys_list):
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

    def append_statistics(self, values, sample_values):
        the_mean = mean(list(map(float, sample_values)))
        the_median = median(list(map(float, sample_values)))
        values.extend((the_mean, the_median))
        return values  

    def process_file_name(self, file_path_object): 
        name_parts = file_path_object.name.split('_')   
        CONST_PART1 = name_parts[:4]
        CONST_PART2 = name_parts[-1]
        rename_part1 = CONST_PART1[0][0] + CONST_PART1[0][-1] + '-' + CONST_PART1[1][0] + CONST_PART1[1][-1] + '-'
        rename_part2 = '-'.join(name_parts[4:-1])   
        rename_part3 = '-' + CONST_PART2[0] + 'p'
        renamed = rename_part1 + rename_part2 + rename_part3 
        return renamed.lower()

fft = FFTProcessor()
fft.activate_process(strict_dir_path='assets')