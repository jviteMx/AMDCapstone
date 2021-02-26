import pandas as pd
from mongo_read import MongoReader

reader = MongoReader()
#Initial db reads
registered_platforms = reader.read_collection(db='AMD_DATA', collection='platform', query={})
registered_platforms = registered_platforms['name'].sort_values().tolist()
registered_data_groups = reader.read_collection(db='AMD_DATA', collection='data_group', query={})
registered_data_groups = registered_data_groups['name'].sort_values().unique()
registered_libraries = reader.read_collection(db='AMD_DATA', collection='rocm', query={})
registered_libraries = registered_libraries['name'].sort_values().unique()

def get_concat_dataframe(platform, dataset, versions):
    dfs = list()
    if 'All' in versions:
        dfs_all = concat_all_collections(platform, dataset)
        return pd.concat(dfs_all)
    for version in versions:
        db = platform
        collection = dataset.lower() + "-rocm" + version
        df = reader.read_collection(db, collection)
        if not df.empty:
            df['rocm version'] = version
            dfs.append(df)
        else:
            continue
    if dfs:        
        return pd.concat(dfs)
    else:
        return pd.DataFrame()

def concat_all_collections(db, dataset):
    dfs_all = list()
    for version in registered_libraries:
        collection = dataset.lower() + "-rocm" + version
        df = reader.read_collection(db, collection)
        if not df.empty:
            df['rocm version'] = version
            dfs_all.append(df)
        else:
            continue    
    return dfs_all

