from mongo_writer import DBInserter

writer = DBInserter()

def register_file_name(name):
    label = name.split('-')[:-1] 
    label = '-'.join(label).upper() 
    collection = writer.write_to_db('AMD_DATA', 'data_group', [{'name': label}])   
    #print(collection.find_one({'name': label}))

def register_new_lib_version(version):
    collection = writer.write_to_db('AMD_DATA', 'rocm', [{'name': version.strip('rocm')}])

def register_new_spec_name(name):
    collection = writer.write_to_db('AMD_DATA', 'platform', [{'name': name}]) 

def write_data_to_mongo(file_path_object, file_name, list_of_dicts):
    collection = writer.write_to_db(file_path_object.parents[1].name, file_name, list_of_dicts)     #Replace with correct db name after resolving with team

def write_spec_data_to_mongo():    #to be implemented
    pass      