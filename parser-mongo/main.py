import argparse
import sys
from pathlib import Path
from statistics import mean, median
import send2trash
from registry import (register_new_spec_name, register_new_lib_version
                      ,register_file_name, write_data_to_mongo)

#writer = DBInserter()
def retrieve_and_parse_files(directory_path_object):
    path_obj = directory_path_object
    register_new_spec_name(path_obj.name)
    print('processing',path_obj.name + ' data....')
    # process_txt_file(dir_obj)
    sub_dirs = [dir_obj for dir_obj in path_obj.iterdir() if dir_obj.is_dir()]
    for dir_obj in sub_dirs:
        print(dir_obj.name)
        register_new_lib_version(dir_obj.name)
        process_dat_files(dir_obj)
            
def process_dat_files(directory_path_object):
    for datFilePathObj in directory_path_object.glob('*.dat'): 
        with datFilePathObj.open() as f:
            data = f.readlines()
            process_data(data, datFilePathObj)
            send2trash.send2trash(datFilePathObj)      

def process_data(list_data, file_path_object):
    data = list_data
    del data[0]
    list_of_dicts = []
    keys = data[0].split()[1:]
    del keys[-1]
    keys.extend(('mean', 'median')) 
    for i in range(1, len(data)):
        values, sample_values = fulfil_dimensionwise_values(data, i, keys)
        values_extended = append_statistics(values, sample_values)
        dict_data = dict(zip(keys, values_extended))
        list_of_dicts.append(dict_data) 
        file_name = process_file_name(file_path_object)
        register_file_name(file_name)
        write_data_to_mongo(file_path_object, file_name, list_of_dicts)

def fulfil_dimensionwise_values(list_data, iter_number, keys_list):
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

def append_statistics(values, sample_values):
    the_mean = mean(list(map(float, sample_values)))
    the_median = median(list(map(float, sample_values)))
    values.extend((the_mean, the_median))
    return values 
   
def process_file_name(file_path_object):
    name_parts = file_path_object.name.split('_')
    CONST_PART1 = name_parts[:4]
    CONST_PART2 = name_parts[-1]
    rename_part1 = CONST_PART1[0][0] + CONST_PART1[0][-1] + '-' + CONST_PART1[1][0] + CONST_PART1[1][-1] + '-'
    rename_part2 = '-'.join(name_parts[4:-1]) 
    rename_part3 = '-' + CONST_PART2[0] + 'p' + '-' + file_path_object.parent.name  
    renamed = rename_part1 + rename_part2 + rename_part3 
    return renamed 

# def process_txt_file(path_object):
#     for textFilePathObj in path_object.glob('*.txt'):     


        
my_parser = argparse.ArgumentParser(description='Parse dat files in all sub directories')
# Add the arguments
my_parser.add_argument('Path',
                       metavar='path',
                       type=str,
                       help='the path containing directories containing .dat files')

args = my_parser.parse_args()

input_path = args.Path

if not Path(input_path).is_dir():
    print('The path specified does not exist')
    sys.exit()

if __name__ == '__main__':
    path_object = Path(input_path)
    spec_dirs = [dir_obj for dir_obj in path_object.iterdir() if dir_obj.is_dir()]
    for spec_path_object in spec_dirs:
        retrieve_and_parse_files(spec_path_object)   
          