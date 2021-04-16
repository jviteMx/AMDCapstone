import numpy as np
import dash_bootstrap_components as dbc
import dash_html_components as html
import model, visuals, specs

selected_library = ''
def check_input_integrity(cell_visual_pair):    #null input, inputs without hardware_id rocm_version test_Suite graph 
    validated_inputs = []
    cell = cell_visual_pair[0]                                                                            
    cell_trio_elements = cell['props']['children'][:-1]
    for i in range(len(cell_trio_elements)):
        cell_trio_element = cell_trio_elements[i]
        field_pair = cell_trio_element['props']['children']['props']['children']['props']['children'][1:]
        try:
            field_type_selected = field_pair[0]['props']['children']['props']['value']
            field_value_selected = field_pair[1]['props']['value']
        except:
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

def group_inputs_by_collection_names(passed_inputs_list):  # gpu-server-1-rocfft-rocm3.9-r5-d3-ratio-1-1-c2c-op
    pass # return several collections based of input permutation

def analyze_single_suite(inputs):
    pass

def analyze_multiple_suites(inputs):
    pass

def analyze_inputs(cell_visual_pair, library): 
    global selected_library
    selected_library = library
    integrity_result = check_input_integrity(cell_visual_pair)
    if not isinstance(integrity_result, list):
        failed = integrity_result
        return failed
    integrity_result = fix_version_all_case(integrity_result)    
    integrity_result = check_for_compulsory_fields(integrity_result) 
    if not isinstance(integrity_result, list):
        failed = integrity_result
        return failed
    integrity_result = check_for_repetition(integrity_result) 
    if not isinstance(integrity_result, list):
        failed = integrity_result
        return failed
    collection_ls = make_possible_collection_permutations(integrity_result) 
    if not isinstance(collection_ls, list):
        failed = collection_ls
        return failed 
    speedup_options = get_speedup_options(integrity_result)  
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
        graph = get_graph(integrity_result)
        if not isinstance(graph, list):
            failed = graph
            return failed    
        versions = get_rocm_versions(integrity_result)
        speedup_options = get_speedup_options(integrity_result) 
        figure, table = visuals.make_graph(concat_df, "Performance Plot", graph, versions, speedup_options) 
        gpu_servers = get_gpu_servers(integrity_result)
        gpu_server_specs = specs.get_specs(gpu_servers, versions)
        if len(speedup_options) > 1:
            return [figure, 'speedup', gpu_server_specs, table]
        else:
            return [figure, gpu_server_specs, table]    
def fix_version_all_case(ls_of_tuples):
    rocm_versions = get_rocm_versions(ls_of_tuples)
    if 'All' in rocm_versions:
        for i in range(len(ls_of_tuples)):
            if ls_of_tuples[i][0] == "Version(s)" and 'All' in ls_of_tuples[i][1]:
                print('all exist')
                rocm_versions = model.get_field_values(selected_library, 'Version(s)') 
                rocm_versions = rocm_versions[:-1]
                tupl_to_ls = list(ls_of_tuples[i])
                tupl_to_ls[1] = rocm_versions
                ls_of_tuples[i] = tuple(tupl_to_ls) 
    print(ls_of_tuples)            
    return ls_of_tuples         
def check_for_compulsory_fields(ls_of_tuples):
    field_types = [item[0] for item in ls_of_tuples]
    if 'HardWare-ID' not in field_types or 'Test-Suite' not in field_types or 'Version(s)' not in field_types or 'Graph' not in field_types:
        error = construct_integrity_fail_message('Must contain HardWare-ID, Test-Suite, Version(s), Graph')
        return error
    return ls_of_tuples
        
def check_for_repetition(ls_of_tuples):
    contains_duplicates = any(ls_of_tuples.count(element) > 1 for element in ls_of_tuples)
    if contains_duplicates:
        error = construct_integrity_fail_message("Duplicated field pair")
        return error
    return ls_of_tuples 

def make_possible_collection_permutations(ls_of_tuples):
    gpu_servers = get_gpu_servers(ls_of_tuples)
    test_suites = get_test_suites(ls_of_tuples)
    rocm_versions = get_rocm_versions(ls_of_tuples)
    if 'All' in rocm_versions:
        rocm_versions = model.get_field_values(selected_library, 'Version(s)')
    library = selected_library.lower()
    gpu_servers, test_suites = check_for_possible_gpu_test_suite_conflict(gpu_servers, test_suites)
    if not isinstance(gpu_servers, list):
        failed = gpu_servers
        return failed
    collections = []
    for server in gpu_servers:
        for rocm_version in rocm_versions:          # gpu-server-1-rocfft-rocm3.9-r5-d3-ratio-1-1-c2c-op
            for suite in test_suites:
                collection = server.lower() + '/' + library + '/' + rocm_version + '/' + suite 
                collections.append(collection)
    return collections

def get_gpu_servers(ls_of_tuples):
    gpu_servers = []
    for i in range(len(ls_of_tuples)):
        if ls_of_tuples[i][0] == "HardWare-ID":
            gpu_servers.append(ls_of_tuples[i][1])
    flattened_gpu_servers = [] 
    ls_elements = [item for item in gpu_servers if isinstance(item, list)] 
    non_ls_elements = [item for item in gpu_servers if not isinstance(item, list)]
    made_list = [[item] for item in non_ls_elements]
    for item in made_list:
        ls_elements.append(item)
    gpu_servers = ls_elements    
    for ls in gpu_servers:
        for item in ls:
            flattened_gpu_servers.append(item)     
    return flattened_gpu_servers  

def get_test_suites(ls_of_tuples):
    test_suites = []
    for i in range(len(ls_of_tuples)):
        if ls_of_tuples[i][0] == "Test-Suite":
            test_suites.append(ls_of_tuples[i][1])
    flattened_test_suites = []   
    ls_elements = [item for item in test_suites if isinstance(item, list)] 
    non_ls_elements = [item for item in test_suites if not isinstance(item, list)]
    made_list = [[item] for item in non_ls_elements]
    for item in made_list:
        ls_elements.append(item)
    test_suites = ls_elements    
    for ls in test_suites:
        for item in ls:
            flattened_test_suites.append(item)         
    return flattened_test_suites 

def get_rocm_versions(ls_of_tuples):
    rocm_versions = []
    for i in range(len(ls_of_tuples)):
        if ls_of_tuples[i][0] == "Version(s)":
            rocm_versions.append(ls_of_tuples[i][1])
    flattened_rocm_versions = []  
    for ls in rocm_versions:
        for item in ls:
            flattened_rocm_versions.append(item)  
    print(flattened_rocm_versions, 'versions')               
    return flattened_rocm_versions 

def check_for_possible_gpu_test_suite_conflict(gpu_servers, test_suites):
    if len(gpu_servers) > 1 and len(test_suites) > 1 and len(np.unique(test_suites)) != len(test_suites):
        error = construct_integrity_fail_message('For multiple GPU server analysis, only one test suite analysis is implementable')
        return error, error
    return gpu_servers, test_suites    

def get_speedup_options(ls_of_tuples):
    speedup_options = []
    multiple_check = 0
    for i in range(len(ls_of_tuples)):
        if ls_of_tuples[i][0] == "SpeedUp-Options":
            multiple_check += 1
            speedup_options.append(ls_of_tuples[i][1])
    if multiple_check > 1:
        error = construct_integrity_fail_message('Multiple speedup option field pair not allowed. Select all applicable in a single field pair')  
        return error      
    flattened_speedup_options = []
    if speedup_options:  
        for ls in speedup_options:
            for item in ls:
                flattened_speedup_options.append(item)   
    print(flattened_speedup_options, 'speedup')                  
    return flattened_speedup_options
        
def get_graph(ls_of_tuples):
    graphs = []
    multiple_check = 0
    for i in range(len(ls_of_tuples)):
        if ls_of_tuples[i][0] == "Graph":
            multiple_check += 1
            graphs.append(ls_of_tuples[i][1])
    if multiple_check > 1:
        error = construct_integrity_fail_message('Multiple Graph field pair not allowed')  
        return error      
    flattened_graphs = []
    if graphs:  
        for ls in graphs:
            for item in ls:
                flattened_graphs.append(item)         
    return flattened_graphs        


[{'props': {'children': {'props': {'id': {'type': 'field-type-dropdown', 'index': 2}, 'options': [{'label': 'Graph', 'value': 'Graph'}, 
{'label': 'HardWare-ID', 'value': 'HardWare-ID'}, {'label': 'SpeedUp-Options', 'value': 'SpeedUp-Options'}, {'label': 'Test-Suite', 'value': 'Test-Suite'}, 
{'label': 'Version(s)', 'value': 'Version(s)'}], 'className': 'pair-type-dropdown', 'placeholder': 'Field Type', 'style': {'border-color': 'dodgerblue'}, 
'search_value': '', 'value': 'Test-Suite'}, 'type': 'Dropdown', 'namespace': 'dash_core_components'}, 'id': 'type-dropdown', 'n_clicks': 2, 
'n_clicks_timestamp': 1617407575727}, 'type': 'Div', 'namespace': 'dash_html_components'}, {'props': {'id': {'type': 'field-value-dropdown', 'index': 2}, 
'options': [{'label': 'r2-d1-c2c-ip', 'value': 'r2-d1-c2c-ip'}, {'label': 'r2-d1-c2c-op', 'value': 'r2-d1-c2c-op'}, {'label': 'r2-d1-inv-r2c-ip', 
'value': 'r2-d1-inv-r2c-ip'}, {'label': 'r2-d1-inv-r2c-op', 'value': 'r2-d1-inv-r2c-op'}, {'label': 'r2-d1-r2c-ip', 'value': 'r2-d1-r2c-ip'}, 
{'label': 'r2-d1-r2c-op', 'value': 'r2-d1-r2c-op'}, {'label': 'r2-d2-inv-ratio-1-r2c-ip', 'value': 'r2-d2-inv-ratio-1-r2c-ip'}, {'label': 'r2-d2-inv-ratio-1-r2c-op',
 'value': 'r2-d2-inv-ratio-1-r2c-op'}, {'label': 'r2-d2-ratio-1-c2c-ip', 'value': 'r2-d2-ratio-1-c2c-ip'}, {'label': 'r2-d2-ratio-1-c2c-op', 
 'value': 'r2-d2-ratio-1-c2c-op'}, {'label': 'r2-d2-ratio-1-r2c-ip', 'value': 'r2-d2-ratio-1-r2c-ip'}, {'label': 'r2-d2-ratio-1-r2c-op', 'value': 'r2-d2-ratio-1-r2c-op'}, 
 {'label': 'r2-d3-inv-ratio-1-1-r2c-ip', 'value': 'r2-d3-inv-ratio-1-1-r2c-ip'}, {'label': 'r2-d3-inv-ratio-1-1-r2c-op', 'value': 'r2-d3-inv-ratio-1-1-r2c-op'},
  {'label': 'r2-d3-ratio-1-1-c2c-ip', 'value': 'r2-d3-ratio-1-1-c2c-ip'}, {'label': 'r2-d3-ratio-1-1-c2c-op', 'value': 'r2-d3-ratio-1-1-c2c-op'}, 
  {'label': 'r2-d3-ratio-1-1-r2c-ip', 'value': 'r2-d3-ratio-1-1-r2c-ip'}, {'label': 'r2-d3-ratio-1-1-r2c-op', 'value': 'r2-d3-ratio-1-1-r2c-op'}, 
  {'label': 'r3-d1-c2c-ip', 'value': 'r3-d1-c2c-ip'}, {'label': 'r3-d1-c2c-op', 'value': 'r3-d1-c2c-op'}, {'label': 'r3-d1-inv-r2c-ip', 'value': 'r3-d1-inv-r2c-ip'}, 
  {'label': 'r3-d1-inv-r2c-op', 'value': 'r3-d1-inv-r2c-op'}, {'label': 'r3-d1-r2c-ip', 'value': 'r3-d1-r2c-ip'}, {'label': 'r3-d1-r2c-op', 'value': 'r3-d1-r2c-op'}, 
  {'label': 'r3-d2-inv-ratio-1-r2c-ip', 'value': 'r3-d2-inv-ratio-1-r2c-ip'}, {'label': 'r3-d2-inv-ratio-1-r2c-op', 'value': 'r3-d2-inv-ratio-1-r2c-op'}, 
  {'label': 'r3-d2-ratio-1-c2c-ip', 'value': 'r3-d2-ratio-1-c2c-ip'}, {'label': 'r3-d2-ratio-1-c2c-op', 'value': 'r3-d2-ratio-1-c2c-op'}, 
  {'label': 'r3-d2-ratio-1-r2c-ip', 'value': 'r3-d2-ratio-1-r2c-ip'}, {'label': 'r3-d2-ratio-1-r2c-op', 'value': 'r3-d2-ratio-1-r2c-op'}, 
  {'label': 'r3-d3-inv-ratio-1-1-r2c-ip', 'value': 'r3-d3-inv-ratio-1-1-r2c-ip'}, {'label': 'r3-d3-inv-ratio-1-1-r2c-op', 'value': 'r3-d3-inv-ratio-1-1-r2c-op'}, 
  {'label': 'r3-d3-ratio-1-1-c2c-ip', 'value': 'r3-d3-ratio-1-1-c2c-ip'}, {'label': 'r3-d3-ratio-1-1-c2c-op', 'value': 'r3-d3-ratio-1-1-c2c-op'}, 
  {'label': 'r3-d3-ratio-1-1-r2c-ip', 'value': 'r3-d3-ratio-1-1-r2c-ip'}, {'label': 'r3-d3-ratio-1-1-r2c-op', 'value': 'r3-d3-ratio-1-1-r2c-op'}, 
  {'label': 'r5-d3-ratio-1-1-c2c-ip', 'value': 'r5-d3-ratio-1-1-c2c-ip'}, {'label': 'r5-d3-ratio-1-1-c2c-op', 'value': 'r5-d3-ratio-1-1-c2c-op'}], 
  'className': 'pair-value-dropdown', 'placeholder': 'Field Value', 'style': {'border-color': 'dodgerblue'}, 'multi': True, 'search_value': '', 
  'value': ['r2-d1-c2c-op']}, 'type': 'Dropdown', 'namespace': 'dash_core_components'}]