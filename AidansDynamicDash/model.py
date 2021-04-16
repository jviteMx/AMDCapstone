import pandas as pd
from mongo_read import MongoReader

reader = MongoReader()

aux_db = 'REG_DATA'
def get_concat_dataframe(ls_of_collections):
    dfs = list() 
    for collection in ls_of_collections:
        db = collection.split('/')[0]
        df = reader.read_collection(db, collection)
        if not df.empty:
            df['collection'] = collection
            dfs.append(df)
        else:
            return ['error', collection]
            # continue
    if dfs:        
        return pd.concat(dfs)
    else:
        return pd.DataFrame()  # return empty dataframe. Effectively return None


def get_field_values(library, field_type):
    collection = library.lower() + field_type.lower() + 'fieldvalue' 
    if field_type == 'SpeedUp-Options':
        collection = library.lower() + 'version(s)fieldvalue'
    df = reader.read_collection(db=aux_db, collection=collection, query={})   #collection=library+field_type
    field_values = df['name'].sort_values().tolist()
    if field_type == 'Version(s)':
        field_values.append('All')
    return field_values

def is_multi_selection(library, field_type):
    return True if field_type in ['Version(s)', 'SpeedUp-Options', 'Test-Suite'] else False

def get_specs(hardware_id, rocm):
    specs = dict()
    collection_host = hardware_id.lower() + '/' + rocm + '/hostspecs'
    collection_device = hardware_id.lower() + '/' + rocm + '/devicespecs'
    host_df = reader.read_collection(db=aux_db, collection=collection_host)
    device_df = reader.read_collection(db=aux_db, collection=collection_device)
    host_ls = host_df.to_dict('records')
    device_ls = device_df.to_dict('records')
    specs['hostname'] = host_ls[0]['hostname']
    specs['cpu_info'] = host_ls[0]['cpu info']
    specs['ram'] = host_ls[0]['ram']
    specs['distro'] = host_ls[0]['distro']
    specs['kernel'] = host_ls[0]['kernel version']
    specs['rocm'] = host_ls[0]['rocm version']
    specs['device'] = device_ls[0]['device']
    specs['vbios']= device_ls[0]['vbios version']
    specs['vram'] = device_ls[0]['vram']
    specs['performance'] = device_ls[0]['performance level']
    specs['sys_clock'] = device_ls[0]['system clock']
    specs['mem_clock'] = device_ls[0]['memory clock']
    return specs

def get_field_types(library):
    collection = library.lower() + 'field_type'
    field_types = reader.read_collection(db=aux_db, collection=collection, query={})
    field_types = field_types['name'].sort_values().tolist()
    return field_types

def get_registered_libraries():
    registered_libraries = reader.read_collection(db=aux_db, collection='libraries', query={})
    registered_libraries = registered_libraries['name'].sort_values().tolist()    
    return registered_libraries