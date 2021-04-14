# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""App center. Specifies the layout dynamically with pattern matching
and also the callbacks
"""

from textwrap import dedent
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State, MATCH
import model
import analysis
import visuals

#register selected library and add_clicks state globally
selected_library = ''
add_clicks_state = 0
visual_pair_state = ''
registered_libraries = model.get_registered_libraries()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                 suppress_callback_exceptions=True)
app.title = "Rocm Analytics: Analyze the performance of libraries"

app.layout = html.Div(
    id={'type':'layout','index':0},
    children=[
        dbc.Jumbotron(html.Div(
            children=[
                # html.P(children="AMD", className="header-emoji"),
                html.P(children=html.Div(html.Img(src=app.get_asset_url('amd.png')))),
                html.H1(
                    children=["MLSE Library Performance Monitor Notebook", html.Span('ish',
                    className='ish',contentEditable='true')], className="header-title"
                ),
                html.P(
                    children="Analyze the performance of rocm math libraries",
                    # " from version 3.6",
                    className="header-description",
                ),
            ],
            className="header",
        ), style={'background-color': '#262b2f'}, fluid=True),  #657786

        html.Div(dbc.Row(
            id={'type':'dynamic-header-menu-container','index':0},
            children=[
                html.Div(dcc.Dropdown(
                    id={
                        'type': 'library-dropdown',
                        'index': 0
                    },
                    options=[{'label': i, 'value': i} for i in registered_libraries],
                    placeholder='Select Library',
                    clearable=False,
                    # style={'background-color': '#FFFFFF'},
                    className='library-dropdown'
                ), id='library-id'),
            ],
            no_gutters=True
        ),className='dynamic-header-menu-container1'),

        html.Div(id={'type':'dynamic-menu-output-container', 'index':1},
                 children=[], className='menu-rows-container'),
    ]
)
@app.callback(
    [Output({'type':'layout', 'index':MATCH}, 'children'),
     Output({'type':'dynamic-header-menu-container', 'index':MATCH}, 'children')
    ],
    Input({'type': 'library-dropdown', 'index':MATCH}, 'value'),
    [State({'type':'dynamic-header-menu-container', 'index':MATCH}, 'children'),
     State({'type':'layout', 'index':MATCH}, 'children')
    ],
    )
def update_header_menu(library, children, layout_children):
    """Updates the header menu with buttons for adding and removing fields."""
    global selected_library
    selected_library = library
    selected_input = dash.callback_context.triggered[0]['value']
    # registered_libraries = model.get_registered_libraries()
    if selected_input in registered_libraries:
        layout_children[2]['props']['children']  = []
        add_field_button = generate_add_field_button()
        remove_field_button = generate_remove_field_button()
        add_row_button = generate_add_row_button()
        remove_row_button = generate_remove_row_button()
        children = [children[0], add_field_button, remove_field_button,
                   add_row_button, remove_row_button]
        layout_children[1]['props']['className'] = 'dynamic-header-menu-container2'
        return [layout_children, children]
    layout_children[1]['props']['className'] = 'dynamic-header-menu-container1'
    children=[children[0]]
    return [layout_children, children]

def generate_add_field_button():
    """Generates and returns button"""
    element = html.Button("+Field", id='dynamic-add-field', n_clicks=0,
                                   className='add-field-button')
    return element

def generate_remove_field_button():
    """Generates and returns button"""
    element = html.Button("-Field", id='dynamic-remove-field', n_clicks=0,
                                   className='remove-field-button')
    return element

def generate_add_row_button():
    """Generates and returns button"""
    element = html.Button("+fieldCell", id='dynamic-add-twin-line', n_clicks=0,
                           className='add-twin-line-button')
    return element
def generate_remove_row_button():
    """Generates and returns button"""
    element = html.Button("-fieldCell", id='dynamic-remove-twin-line',
                       n_clicks=0, className='remove-twin-line-button')
    return element
@app.callback(
    Output({'type':'dynamic-menu-output-container', 'index':1}, 'children'),
    [Input('dynamic-add-field', 'n_clicks'),
     Input('dynamic-remove-field', 'n_clicks'),
     Input('dynamic-add-twin-line', 'n_clicks'),
     Input('dynamic-remove-twin-line', 'n_clicks')
    ],
    State({'type':'dynamic-menu-output-container', 'index':1}, 'children'),
    prevent_initial_call=True
)
def add_remove_field(add_button_clicks, _, ___, ____, rows_div_children):
    """Adds field pair to row"""
    global add_clicks_state
    add_clicks_state = add_clicks_state + 1
    ctx = dash.callback_context
    if (add_button_clicks == 0 and (ctx.triggered[0]['prop_id'].split('.')[0]\
        !="dynamic-remove-field" and ctx.triggered[0]['prop_id'].split('.')[0]\
        !="dynamic-add-twin-line" and ctx.triggered[0]['prop_id'].split('.')[0]\
        !="dynamic-remove-twin-line")) or \
            (ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0]=="dynamic-add-field"):
        clicks_num = add_clicks_state
        field_pair = generate_field_pair(clicks_num)
        if len(rows_div_children) < 1:
            row_level_buttons = generate_row_level_buttons(clicks_num)
            new_row = html.Div(children=[dbc.Row(children=
                [dbc.Col(field_pair,xs=6, md=4, lg=3, xl=2),
                dbc.Col(row_level_buttons,xs=6, md=4, lg=3, xl=2, align='center')],
                style={'background-color': '#AAB8C2', 'margin-top': '-12px', 'border-bottom': '2px solid #ffcccb'}),
                html.Div(children=[], id={'type':'md+graphs-rows', 'index':clicks_num})
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
            value = rows_div_children[-1]['props']['children'][0]['props']['children'][-2]['props']['children']['props']['children']['props']['children'][1]['props']['value']
        except:
            value = 'none'
        if value != 'none':
            rows_div_children[-1]['props']['children'][1]['props']['children']  = []
        try:
            rows_div_children[-1]['props']['children'][0]['props']['children'].pop(-2)
        except:
            pass
        return rows_div_children
    elif (ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0]=="dynamic-add-twin-line"):
        if len(rows_div_children) == 0:
            style={'background-color': '#AAB8C2', 'margin-top': '-12px', 'border-bottom': '2px solid #ffcccb'}
        else:
            style={'background-color': '#AAB8C2', 'margin-top': '1px', 'border-bottom': '2px solid #ffcccb'}
        clicks_num = add_clicks_state
        field_pair = generate_field_pair(clicks_num)
        row_level_buttons = generate_row_level_buttons(clicks_num)
        new_row = html.Div(children=[dbc.Row(children=[dbc.Col(field_pair,xs=6, md=4, lg=3, xl=2),
                 dbc.Col(row_level_buttons,xs=6, md=4, lg=3, xl=2, align='center')], style=style),
            html.Div(children=[], id={'type':'md+graphs-rows', 'index':clicks_num})    
        ],
            id={'type':'row+visual-div', 'index':clicks_num}
        )
        rows_div_children.append(new_row)   
        return rows_div_children 
    elif (ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0]=="dynamic-remove-twin-line") and len(rows_div_children) > 0:
        rows_div_children.pop()       
        return rows_div_children       
    return rows_div_children           

def generate_field_pair(num_clicks):
    library = selected_library                
    options = model.get_field_types(library)
    options = [{'label': item, 'value': item} for item in options] 
    field_pair = html.Div(html.Div(id={'type': 'field-dropdown', 'index': num_clicks}, children=[
        html.Button('x', id={'type': 'self-remove', 'index': num_clicks}, className='self-remove-button', n_clicks=0),
        html.Div(dcc.Dropdown(
            id={'type': 'field-type-dropdown', 'index': num_clicks},
            options=options,
            placeholder='Field Type',
            # clearable=False,
            className='pair-type-dropdown',
            style={'border-color': 'dodgerblue'}
        ), id='type-dropdown'),
        dcc.Dropdown(
            id={'type':'field-value-dropdown', 'index': num_clicks},
            options=[{'label':'Select Type', 'value':'Select Type', 'disabled':True, 'title': 'Select field type first'}],
            placeholder='Field Value',
            # clearable=False,
            optionHeight=40,
            className='pair-value-dropdown',
            style={'border-color': 'dodgerblue'}
        )],
        className='dropdown-pair'
    ), id='field-dropdown')
    return field_pair

def generate_row_level_buttons(num_clicks):
    buttons = html.Div(id={'type': 'row-level-buttons', 'index': num_clicks},
        children=[html.Button("x", id={'type':'row-remove-field','index':num_clicks}, n_clicks=0, className='row-level-remove-field'),
                  html.Button("+", id={'type':'row-add-field','index':num_clicks}, n_clicks=0, className='row-level-add-field'),
                  html.Button("Analyze", id={'type':'row-analyze-button','index':num_clicks}, n_clicks=0, className='row-level-analyze-button'),
                  html.Button("/", id={'type':'row-toggle-button','index':num_clicks}, n_clicks=0, className='row-level-toggle')
        ],
        className='row-level-buttons'
    )
    return buttons

@app.callback(
    [Output({'type':'field-value-dropdown', 'index':MATCH}, 'options'),
     Output({'type':'field-value-dropdown', 'index':MATCH}, 'multi')
    ],
    Input({'type': 'field-type-dropdown', 'index':MATCH}, 'value'),
    [State({'type':'field-type-dropdown', 'index':MATCH}, 'id'),
     State({'type':'field-value-dropdown', 'index':MATCH}, 'options'),
     State({'type':'field-value-dropdown', 'index':MATCH}, 'multi')
    ],
    prevent_initial_call=True
)   
def update_library_field_value(field_type, _, field_value_options, is_multi_selection):
    if field_type is None:
        field_value_options = [{'label':'Select Type', 'value':'Select Type', 'disabled':True, 'title': 'Select field type first'}]
        return [field_value_options, is_multi_selection] 
    library = selected_library
    options = model.get_field_values(library, field_type)       
    options = [{'label': item, 'value': item} for item in options]
    is_multi= model.is_multi_selection(library, field_type)
    if is_multi:
        is_multi_selection = True

    return [options, is_multi_selection]

@app.callback(
    Output({'type':'row+visual-div', 'index':MATCH}, 'children'),
    [
     Input({'type':'row-remove-field', 'index':MATCH}, 'n_clicks'),
     Input({'type':'row-add-field','index':MATCH}, 'n_clicks'),
     Input({'type':'row-analyze-button','index':MATCH}, 'n_clicks'),
     Input({'type':'row-toggle-button','index':MATCH}, 'n_clicks'),
    ],
    State({'type':'row+visual-div', 'index':MATCH}, 'children'),
    prevent_initial_call=True
)   
def analyze_row_cell(_, __, ___, ____, row_visual_pair):
    global add_clicks_state
    add_clicks_state = add_clicks_state + 1
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0].split(':')[2].strip('}"')
    if triggered_id == "row-add-field":
        field_pair = generate_field_pair(add_clicks_state)
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
        visual_output = analysis.analyze_inputs(row_visual_pair, selected_library)
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
                                 no_gutters=True, justify='start', className='analyze-output', id={'type': 'spec-info', 'index':add_clicks_state})
            children = [plot, table]
            id={'type':'output-visuals', 'index':add_clicks_state}
            if selected_library.lower() == 'rocrand':
                children = visuals.add_rand_slider(children, add_clicks_state)
            elif selected_library.lower() == 'rocblas':
                children = visuals.add_blas_slider(children, add_clicks_state)
                id={'type':'output-visuals-blas', 'index':add_clicks_state}                        
            visuals_out =  dbc.Row(children=children, justify='start', className='analyze-output plots', id=id)
            try:
                row_visual_pair[1]['props']['children']  = [specs_out, visuals_out] 
            except:
                pass
        else:
            error =  dbc.Col(html.Div(visual_output, className='analyze-output'), xs=3, lg=2)
            row_visual_pair[1]['props']['children']  = [dbc.Row(children=[error], justify='end')]
    elif triggered_id == 'row-toggle-button':
        row_visual_pair[1]['props']['children']  = []
    else:
        return row_visual_pair

    return row_visual_pair

@app.callback(
    Output({'type':'output-visuals', 'index':MATCH}, 'children'),
    Input({'type':'slider', 'index':MATCH}, 'value'),
    State({'type':'output-visuals', 'index':MATCH}, 'children'),
    prevent_initial_call=True
)
def make_rand_slider_plot(slide, visual_state):
    visual_output = visuals.make_rand_slider_plot(slide)
    visual_output = dcc.Graph(figure=visual_output)
    visual_state[0] = dbc.Col(visual_output, xs=12, md=8, className='card-size')
    return visual_state

@app.callback(
    Output({'type':'output-visuals-blas', 'index':MATCH}, 'children'),
    Input({'type':'blas-slider', 'index':MATCH}, 'value'),
    State({'type':'output-visuals-blas', 'index':MATCH}, 'children'),
    prevent_initial_call=True
)
def make_blas_slider_plot(slide, visual_state):
    fig, table = visuals.make_blas_slider_plot(slide)
    visual_output = dcc.Graph(figure=fig)
    visual_state[0] = dbc.Col(visual_output, xs=12, md=8, className='card-size')
    visual_state[1] = dbc.Col(table, xs=12, md=8)
    return visual_state

if __name__ == "__main__":
    app.run_server(debug=True)
