# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Serves as app data engine. providing all data in the required form"""
import pandas as pd
from mongo_read import MongoReader

reader = MongoReader()

AUX_DB = 'aux-db'
def get_concat_dataframe(ls_of_collections):
    """Queries database for related collections and returns concatenated
    dataframes
    """
    dfs = list()
    for collection in ls_of_collections:
        database = collection.split('/')[0]
        frame = reader.read_collection(database, collection)
        if not frame.empty:
            frame['collection'] = collection
            dfs.append(frame)
        else:
            return ['error', collection]
    if dfs:
        return pd.concat(dfs)
    return pd.DataFrame()  # return empty dataframe. Effectively return None


def get_field_values(library, field_type):
    """Returns list of field values for selected field type"""
    collection = library.lower() + field_type.lower() + 'fieldvalue'
    if field_type == 'SpeedUp-Options':
        collection = library.lower() + 'version(s)fieldvalue'
    frame = reader.read_collection(AUX_DB, collection=collection)
    field_values = frame['name'].sort_values().tolist()
    if field_type == 'Version(s)':
        field_values.append('All')
    return field_values

def is_multi_selection(library, field_type):
    """Some field value dropdowns are multi select"""
    _ = library #No need to query db. Same always for now and not super useful
    return True if field_type in \
    ['Version(s)', 'SpeedUp-Options', 'Test-Suite', 'Algorithm'] else False

def get_specs(hardware_id, rocm):
    """Quries db for rocm hardware specs and returns a dictionary of it"""
    specs = dict()
    collection_host = hardware_id.lower() + '/' + rocm + '/hostspecs'
    collection_device = hardware_id.lower() + '/' + rocm + '/devicespecs'
    host_df = reader.read_collection(AUX_DB, collection=collection_host)
    device_df = reader.read_collection(AUX_DB, collection=collection_device)
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
    """Quries db for the registered dropdown field types for selected library
    and returns the list"""
    collection = library.lower() + 'field_type'
    field_types = reader.read_collection(AUX_DB, collection=collection)
    field_types = field_types['name'].sort_values().tolist()
    return field_types

def get_registered_libraries():
    """Queries the db for all registered libraries and returns the list"""
    registered_libraries = reader.read_collection(AUX_DB, collection='libraries')
    registered_libraries = registered_libraries['name'].sort_values().tolist()
    return registered_libraries
