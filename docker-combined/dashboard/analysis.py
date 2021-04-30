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

"""Analyzes the field inputs for integrity check and initiate process to make plot analysis"""

import numpy as np
import dash_bootstrap_components as dbc
import dash_html_components as html
import model
import visuals
import specs

def check_input_integrity(cell_visual_pair):
    validated_inputs = []
    cell = cell_visual_pair[0]                                                                            
    cell_trio_elements = cell['props']['children'][:-1]
    for i in range(len(cell_trio_elements)):
        cell_trio_element = cell_trio_elements[i]
        field_pair = cell_trio_element['props']['children']['props']['children']['props']['children'][1:]
        try:
            field_type_selected = field_pair[0]['props']['children']['props']['value']
            field_value_selected = field_pair[1]['props']['value']
        except KeyError:
            message = 'Unselected dropdowns'
            error = construct_integrity_fail_message(message)
            return error
        if not field_value_selected:
            message = f'Unselected {field_type_selected} field value dropdown'
            error = construct_integrity_fail_message(message)
            return error  
        validated_inputs.append((field_type_selected, field_value_selected))
    return validated_inputs        

def construct_integrity_fail_message(error):
    error_toast = dbc.Toast(
            [html.P(error, className="mb-0")],
            id="simple-toast",
            header="All not good \U0001F616",
            icon="danger",
            dismissable=True,
        )
    return error_toast

def analyze_inputs(cell_visual_pair, library):
    integrity_result = check_input_integrity(cell_visual_pair)
    if not isinstance(integrity_result, list):
        failed = integrity_result
        return failed
    integrity_result = fix_version_all_case(integrity_result, library)
    integrity_result = check_for_compulsory_fields(integrity_result, library)
    if not isinstance(integrity_result, list):
        failed = integrity_result
        return failed
    inputs = integrity_result[0]
    extras = integrity_result[1]    
    integrity_result = check_for_repetition(inputs)
    if not isinstance(integrity_result, list):
        failed = integrity_result
        return failed
    collection_ls = make_possible_collection_permutations(inputs, library)
    if not isinstance(collection_ls, list):
        failed = collection_ls
        return failed
    speedup_options = get_speedup_options(inputs)
    if not isinstance(speedup_options, list):
        failed = speedup_options
        return failed
    concat_df = model.get_concat_dataframe(collection_ls)
    if isinstance(concat_df, list):
        failed = construct_integrity_fail_message(concat_df[1] + ' is not a valid suite existing in database')
        return failed
    if concat_df.empty:
        failed = construct_integrity_fail_message('Nothing found for selection')   
        return failed
    else:
        graph = get_graph(inputs)
        if not isinstance(graph, list):
            failed = graph
            return failed
        versions = get_rocm_versions(inputs)
        speedup_options = get_speedup_options(inputs) 
        figure, table = visuals.make_graph_table(concat_df, "Performance Plot", graph[0], versions, speedup_options, library, extras=extras) 
        gpu_servers = get_gpu_servers(inputs)
        gpu_server_specs = specs.get_specs(gpu_servers, versions)
        if len(speedup_options) > 1 or library.lower() == 'rocblas':
            return [figure, 'speedup', gpu_server_specs, table]
        else:
            return [figure, gpu_server_specs, table]    
def fix_version_all_case(ls_of_tuples, library):
    rocm_versions = get_rocm_versions(ls_of_tuples)
    if 'All' in rocm_versions:
        for i, data in enumerate(ls_of_tuples):
            if data[0] == "Version(s)" and 'All' in data[1]:
                rocm_versions = model.get_field_values(library, 'Version(s)')
                rocm_versions = rocm_versions[:-1]
                tupl_to_ls = list(data)
                tupl_to_ls[1] = rocm_versions
                ls_of_tuples[i] = tuple(tupl_to_ls)
    return ls_of_tuples         
def check_for_compulsory_fields(ls_of_tuples, library):
    added = False
    field_types = [item[0] for item in ls_of_tuples]
    if library.lower() == 'rocrand' and  'Algorithm' not in field_types:
        error =  construct_integrity_fail_message('Must contain HardWare-ID, Test-Suite, Version(s), Graph, Algorithm')
        return error
    if  library.lower() == 'rocrand':
        extras = [item[1] for item in ls_of_tuples if item[0]=='Algorithm']    
        extras = [item for sublist in extras for item in sublist]
        added = True 

    if 'HardWare-ID' not in field_types or 'Test-Suite' not in field_types or 'Version(s)' not in field_types or 'Graph' not in field_types:
        error = construct_integrity_fail_message('Must contain HardWare-ID, Test-Suite, Version(s), Graph')
        return error
    if added:
        return [ls_of_tuples, extras]    
    return [ls_of_tuples, []]
        
def check_for_repetition(ls_of_tuples):
    contains_duplicates = any(ls_of_tuples.count(element) > 1 for element in ls_of_tuples)
    if contains_duplicates:
        error = construct_integrity_fail_message("Duplicated field pair")
        return error
    return ls_of_tuples 

def make_possible_collection_permutations(ls_of_tuples, library):
    gpu_servers = get_gpu_servers(ls_of_tuples)
    test_suites = get_test_suites(ls_of_tuples)
    rocm_versions = get_rocm_versions(ls_of_tuples)
    if 'All' in rocm_versions:
        rocm_versions = model.get_field_values(library, 'Version(s)')
    library = library.lower()
    gpu_servers, test_suites = check_for_possible_gpu_test_suite_conflict(gpu_servers, test_suites)
    if not isinstance(gpu_servers, list):
        failed = gpu_servers
        return failed
    collections = []
    for server in gpu_servers:
        for rocm_version in rocm_versions:
            for suite in test_suites:
                collection = server.lower() + '/' + library + '/' + rocm_version + '/' + suite
                collections.append(collection)
    return collections

def get_gpu_servers(ls_of_tuples):
    gpu_servers = []
    for _, data in enumerate(ls_of_tuples):
        if data[0] == "HardWare-ID":
            gpu_servers.append(data[1])
    ls_elements = [item for item in gpu_servers if isinstance(item, list)] 
    non_ls_elements = [item for item in gpu_servers if not isinstance(item, list)]
    made_list = [[item] for item in non_ls_elements]
    for item in made_list:
        ls_elements.append(item)
    gpu_servers = ls_elements
    flattened_gpu_servers = [item for sublist in gpu_servers for item in sublist]
    return flattened_gpu_servers

def get_test_suites(ls_of_tuples):
    test_suites = []
    for _, data in enumerate(ls_of_tuples):
        if data[0] == "Test-Suite":
            test_suites.append(data[1])  
    ls_elements = [item for item in test_suites if isinstance(item, list)]
    non_ls_elements = [item for item in test_suites if not isinstance(item, list)]
    made_list = [[item] for item in non_ls_elements]
    for item in made_list:
        ls_elements.append(item)
    test_suites = ls_elements 
    flattened_test_suites = [item for sublist in test_suites for item in sublist]
    return flattened_test_suites

def get_rocm_versions(ls_of_tuples):
    rocm_versions = []
    for _, data in enumerate(ls_of_tuples):
        if data[0] == "Version(s)":
            rocm_versions.append(data[1])
    flattened_rocm_versions = [item for sublist in rocm_versions for item in sublist]
    return flattened_rocm_versions

def check_for_possible_gpu_test_suite_conflict(gpu_servers, test_suites):
    if len(gpu_servers) > 1 and len(test_suites) > 1 and len(np.unique(test_suites)) != len(test_suites):
        error = construct_integrity_fail_message('For multiple GPU server analysis, only one test suite analysis is implementable')
        return error, error
    return gpu_servers, test_suites

def get_speedup_options(ls_of_tuples):
    speedup_options = []
    multiple_check = 0
    for _, data in enumerate(ls_of_tuples):
        if data[0] == "SpeedUp-Options":
            multiple_check += 1
            speedup_options.append(data[1])
    if multiple_check > 1:
        error = construct_integrity_fail_message('Multiple speedup option field pair not allowed. Select all applicable in a single field pair')
        return error
    flattened_speedup_options = []
    if speedup_options:
        flattened_speedup_options = [item for sublist in speedup_options for item in sublist]                  
    return flattened_speedup_options

def get_graph(ls_of_tuples):
    graphs = []
    multiple_check = 0
    for _, data in enumerate(ls_of_tuples):
        if data[0] == "Graph":
            multiple_check += 1
            graphs.append(data[1])
    if multiple_check > 1:
        error = construct_integrity_fail_message('Multiple Graph field pair not allowed')
        return error
    return graphs
