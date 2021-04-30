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

"""App center. Specifies the layout dynamically with pattern matching
and also the callbacks
"""

from textwrap import dedent
import json
import uuid
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State, MATCH
import layout
import model
import analysis
import visuals

app = layout.app
@app.callback(
    [Output('layout', 'children'),
     Output('dynamic-header-menu-container', 'children'),
     Output('intermediate-library-value', 'children')
    ],
    Input('libraries-dropdown', 'value'),
    [State('dynamic-header-menu-container', 'children'),
     State('intermediate-library-value', 'children'),
     State('layout', 'children')
    ]
)
def update_header_menu(library, children, _, layout_children):
    """Updates the header menu with buttons for adding and removing fields."""
    selected_library = library
    selected_input = dash.callback_context.triggered[0]['value']
    if selected_input in model.get_registered_libraries():
        layout_children[2]['props']['children']  = []
        add_field_button = visuals.generate_add_field_button()
        remove_field_button = visuals.generate_remove_field_button()
        add_row_button = visuals.generate_add_row_button()
        remove_row_button = visuals.generate_remove_row_button()
        children = [children[0], add_field_button, remove_field_button,
                   add_row_button, remove_row_button]
        layout_children[1]['props']['className'] = 'dynamic-header-menu-container2'
        return [layout_children, children, json.dumps(selected_library)]    
    layout_children[1]['props']['className'] = 'dynamic-header-menu-container1'
    children=[children[0]]
    return [layout_children, children, json.dumps(selected_library)]

@app.callback(
    Output({'type':'dynamic-menu-output-container', 'index':1}, 'children'),
    [Input('dynamic-add-field', 'n_clicks'),
     Input('dynamic-remove-field', 'n_clicks'),
     Input('dynamic-add-twin-line', 'n_clicks'),
     Input('dynamic-remove-twin-line', 'n_clicks'),
     Input('intermediate-library-value', 'children')
    ],
    State({'type':'dynamic-menu-output-container', 'index':1}, 'children'),
    prevent_initial_call=True
)
def add_remove_field_or_cell(add_button_clicks, _, ___, ____, jsonified_selected_lib, rows_div_children):
    """Adds field pair to row"""
    clicks_num = uuid.uuid4().int
    clicks_num = int(str(clicks_num)[-10:-1])
    ctx = dash.callback_context
    if (add_button_clicks == 0 and (ctx.triggered[0]['prop_id'].split('.')[0]\
        !="dynamic-remove-field" and ctx.triggered[0]['prop_id'].split('.')[0]\
        !="dynamic-add-twin-line" and ctx.triggered[0]['prop_id'].split('.')[0]\
        !="dynamic-remove-twin-line")) or \
            (ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0]=="dynamic-add-field"):
        field_pair = visuals.generate_field_pair(clicks_num, json.loads(jsonified_selected_lib))
        if len(rows_div_children) < 1:
            row_level_buttons = visuals.generate_row_level_buttons(clicks_num)
            new_row = html.Div(children=[dbc.Row(children=
                [dbc.Col(field_pair,xs=6, md=4, lg=3, xl=2),
                dbc.Col(row_level_buttons,xs=6, md=4, lg=3, xl=2, align='center')],
                style={'background-color': '#AAB8C2', 'margin-top': '-12px', 'border-bottom': '2px solid #ffcccb'}),
                html.Div(children=[], id={'type':'md+graphs-rows', 'index':clicks_num}),
                html.Div(id={'type':'intermediate-visual-state', 'index':clicks_num}, style={'display': 'none'}),
            ],
                id={'type':'row+visual-div', 'index':clicks_num}
            )

            rows_div_children.append(new_row)
        else:
            temp = rows_div_children[-1]['props']['children'][0]['props']['children'].pop()
            rows_div_children[-1]['props']['children'][0]['props']['children']\
                .extend((dbc.Col(field_pair, xs=6, md=4, lg=3, xl=2),temp))
    elif (ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0]=="dynamic-remove-field")\
         and len(rows_div_children) > 0 and len(rows_div_children[-1]['props']['children'][0]['props']['children'])>=1:
                                                                                      
        try:
            #Need to refactor with dictionary query tool like JMESPath
            value = rows_div_children[-1]['props']['children'][0]['props']['children'][-2]['props']['children']['props']['children']['props']['children'][1]['props']['value']
        except IndexError:
            value = None
        except KeyError:
            value = None
        if value is not None:
            rows_div_children[-1]['props']['children'][1]['props']['children']  = []
        try:
            rows_div_children[-1]['props']['children'][0]['props']['children'].pop(-2)
        except IndexError:
            pass
        return rows_div_children
    elif (ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0]=="dynamic-add-twin-line"):
        if len(rows_div_children) == 0:
            style={'background-color': '#AAB8C2', 'margin-top': '-12px', 'border-bottom': '2px solid #ffcccb'}
        else:
            style={'background-color': '#AAB8C2', 'margin-top': '1px', 'border-bottom': '2px solid #ffcccb'}
        field_pair = visuals.generate_field_pair(clicks_num, json.loads(jsonified_selected_lib))
        row_level_buttons = visuals.generate_row_level_buttons(clicks_num)
        new_row = html.Div(children=[dbc.Row(children=[dbc.Col(field_pair,xs=6, md=4, lg=3, xl=2),
                 dbc.Col(row_level_buttons,xs=6, md=4, lg=3, xl=2, align='center')], style=style),
            html.Div(children=[], id={'type':'md+graphs-rows', 'index':clicks_num}),
            html.Div(id={'type':'intermediate-visual-state', 'index':clicks_num}, style={'display': 'none'}),
        ],
            id={'type':'row+visual-div', 'index':clicks_num}
        )
        rows_div_children.append(new_row)
        return rows_div_children
    elif (ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0]=="dynamic-remove-twin-line") and len(rows_div_children) > 0:
        rows_div_children.pop()
        return rows_div_children
    return rows_div_children

@app.callback(
    [Output({'type':'field-value-dropdown', 'index':MATCH}, 'options'),
     Output({'type':'field-value-dropdown', 'index':MATCH}, 'multi')
    ],
    [Input({'type': 'field-type-dropdown', 'index':MATCH}, 'value'),
     Input('intermediate-library-value', 'children')
    ],
    [State({'type':'field-type-dropdown', 'index':MATCH}, 'id'),
     State({'type':'field-value-dropdown', 'index':MATCH}, 'options'),
     State({'type':'field-value-dropdown', 'index':MATCH}, 'multi')
    ],
    prevent_initial_call=True
)   
def update_library_field_value(field_type, jsonified_selected_lib, _, field_value_options, is_multi_selection):
    if field_type is None:
        field_value_options = [{'label':'Select Type', 'value':'Select Type', 'disabled':True, 'title': 'Select field type first'}]
        return [field_value_options, is_multi_selection]
    library = json.loads(jsonified_selected_lib)
    options = model.get_field_values(library, field_type)
    options = [{'label': item, 'value': item} for item in options]
    is_multi= model.is_multi_selection(library, field_type)
    if is_multi:
        is_multi_selection = True

    return [options, is_multi_selection]

@app.callback(
    [Output({'type':'row+visual-div', 'index':MATCH}, 'children'),
     Output({'type':'intermediate-visual-state', 'index':MATCH}, 'children')
    ],
    [
     Input({'type':'row-remove-field', 'index':MATCH}, 'n_clicks'),
     Input({'type':'row-add-field','index':MATCH}, 'n_clicks'),
     Input({'type':'row-analyze-button','index':MATCH}, 'n_clicks'),
     Input({'type':'row-toggle-button','index':MATCH}, 'n_clicks'),
     Input('intermediate-library-value', 'children')
    ],
    [State({'type':'row+visual-div', 'index':MATCH}, 'children'),
     State({'type':'intermediate-visual-state', 'index':MATCH}, 'children')
    ],
    prevent_initial_call=True
)   
def analyze_or_alter_row_cell(_, __, ___, ____, jsonified_selected_lib, row_visual_pair, visual_save):
    num_clicks = uuid.uuid4().int
    num_clicks = int(str(num_clicks)[-11:-1])
    ctx = dash.callback_context
    try:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0].split(':')[2].strip('}"')
        triggered_idx = ctx.triggered[0]['prop_id'].split('.')[0].split(':')[1].split(',')[0]
    except IndexError:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == "row-add-field":
        field_pair = visuals.generate_field_pair(num_clicks, json.loads(jsonified_selected_lib))
        row_visual_pair[0]['props']['children'] = [*row_visual_pair[0]['props']['children'][:-1],
                            dbc.Col(field_pair, xs=6, md=4, lg=3, xl=2), row_visual_pair[0]['props']['children'][-1]]
    elif triggered_id == 'row-remove-field':
        if len(row_visual_pair[0]['props']['children']) > 1:
            try:
                value = row_visual_pair[0]['props']['children'][-2]['props']['children']['props']['children']['props']['children'][1]['props']['value']
            except KeyError:
                value = 'none'
            if value != 'none':
                row_visual_pair[1]['props']['children']  = []
            row_visual_pair[0]['props']['children'].pop(-2)
        else:
            pass

    elif triggered_id == 'row-analyze-button':
        analyze_clicks = triggered_idx
        visual_output = analysis.analyze_inputs(row_visual_pair, json.loads(jsonified_selected_lib))
        if isinstance(visual_output, list):
            visual_output1 = visual_output[0]
            visual_output1 = dcc.Graph(figure=visual_output1)
            if visual_output[1] == 'speedup':
                table = visual_output[-1]
                gpu_server_specs = visual_output[2]
                plot = dbc.Col(visual_output1, xs=12, md=8, className='card-size')
                table = dbc.Col(table, xs=12, md=8)
            else:
                gpu_server_specs = visual_output[1]
                plot = dbc.Col(visual_output1, xs=12, md=8)
                table = dbc.Col(xs=12, md=8)
            gpu_server_specs = [dcc.Markdown(dedent(gpu_server_spec)) for gpu_server_spec in gpu_server_specs]
            if len(gpu_server_specs) % 3 == 0:
                className = 'gpu-specs-full-row'
                width = 4
            else:
                className = 'gpu-specs-col'
                width = 8
                if len(gpu_server_specs) % 2 == 0:
                    width = 4
                    className = 'gpu-specs-col2'
            specs_out = dbc.Row(children=[dbc.Col(spec_info, width=width, className=className) for spec_info in gpu_server_specs],
                                 no_gutters=True, justify='start', className='analyze-output', id={'type': 'spec-info', 'index':analyze_clicks})
            children = [plot, table]
            visual_id={'type':'output-visuals', 'index':analyze_clicks}
            if json.loads(jsonified_selected_lib).lower() == 'rocrand':
                visual_id={'type':'output-visuals-rand', 'index':analyze_clicks}
                children = visuals.add_rand_slider(children, analyze_clicks)
                outcome = get_what_to_save(row_visual_pair, json.loads(jsonified_selected_lib).lower())
                visual_save = json.dumps(outcome)
            elif json.loads(jsonified_selected_lib).lower() == 'rocblas':
                children = visuals.add_blas_slider(children, analyze_clicks)
                visual_id={'type':'output-visuals-blas', 'index':analyze_clicks}
                outcome = get_what_to_save(row_visual_pair, json.loads(jsonified_selected_lib).lower())
                visual_save = json.dumps(outcome)            
            visuals_out =  dbc.Row(children=children, justify='start', className='analyze-output plots', id=visual_id)
            try:
                row_visual_pair[1]['props']['children']  = [specs_out, visuals_out]
            except IndexError:
                pass
            except ValueError:
                pass
            except KeyError:
                pass
        else:
            error =  dbc.Col(html.Div(visual_output, className='analyze-output'), xs=3, lg=2)
            row_visual_pair[1]['props']['children']  = [dbc.Row(children=[error], justify='end')]
    elif triggered_id == 'row-toggle-button':
        row_visual_pair[1]['props']['children']  = []
    else:
        return [row_visual_pair, visual_save]

    return [row_visual_pair, visual_save]

@app.callback(
    Output({'type':'output-visuals-rand', 'index':MATCH}, 'children'),
    [Input({'type':'rand-slider', 'index':MATCH}, 'value'),
     Input({'type':'intermediate-visual-state','index':MATCH}, 'children')
    ],
    State({'type':'output-visuals-rand', 'index':MATCH}, 'children'),
    prevent_initial_call=True
)
def make_rand_slider_plot(slide, jsonified_obj, visual_state):
    jsonified_obj = json.loads(jsonified_obj)
    frame = pd.read_json(jsonified_obj[0], orient='split')
    algos = jsonified_obj[1]
    visual_output = visuals.make_rand_slider_plot(slide, frame, algos)
    visual_output = dcc.Graph(figure=visual_output)
    visual_state[0] = dbc.Col(visual_output, xs=12, md=8, className='card-size')
    return visual_state

@app.callback(
    Output({'type':'output-visuals-blas', 'index':MATCH}, 'children'),
    [Input({'type':'blas-slider', 'index':MATCH}, 'value'),
     Input({'type':'intermediate-visual-state','index':MATCH}, 'children')
    ],
    State({'type':'output-visuals-blas', 'index':MATCH}, 'children'),
    prevent_initial_call=True
)
def make_blas_slider_plot(slide, jsonified_obj, visual_state):
    jsonified_obj = json.loads(jsonified_obj)
    frame = pd.read_json(jsonified_obj[0], orient='split')
    blas_graph = jsonified_obj[1][0]
    blas_versions = jsonified_obj[2]
    blas_speedup_options = jsonified_obj[3]
    fig, table = visuals.make_blas_slider_plot(slide, frame, blas_graph, blas_versions, blas_speedup_options)
    visual_output = dcc.Graph(figure=fig)
    visual_state[0] = dbc.Col(visual_output, xs=12, md=8, className='card-size')
    visual_state[1] = dbc.Col(table, xs=12, md=8)
    return visual_state


def get_what_to_save(cell_visual_pair, library):
    """Returns what we want to save in user browser browser session
    using the power of json and hiding div mechanism.
    This way we avoid using global variables. Customized for blas and rand
    as we use slider. We must save some data so that we don't query database
    for all slider point callbacks.
    """
    inputs = analysis.check_input_integrity(cell_visual_pair)
    inputs = analysis.fix_version_all_case(inputs, library)
    inputs = analysis.check_for_compulsory_fields(inputs, library)
    inputts = inputs[0]
    extras = inputs[1]
    collection_ls = analysis.make_possible_collection_permutations(inputts, library)
    concat_df = model.get_concat_dataframe(collection_ls)
    df_json = concat_df.to_json(date_format='iso', orient='split')
    graph = analysis.get_graph(inputts)
    versions = analysis.get_rocm_versions(inputts)
    speedup_options = analysis.get_speedup_options(inputts)
    if library == 'rocblas':
        blas_return = [df_json, graph, versions, speedup_options]
        return blas_return
    return [df_json, extras]

if __name__ == "__main__":
    app.run_server(debug=True, port=8082, host="0.0.0.0")