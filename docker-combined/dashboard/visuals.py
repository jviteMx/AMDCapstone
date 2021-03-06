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

"""Where all dashboard data visualization objects are cooked. Plots and tables, 
Non static layout components.
"""

import copy
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash_table.Format import Format, Scheme
from databars_recipes import data_bars_diverging
import model


def make_graph_table(dataframe, title, graph, versions, speedup_options, library, extras=None):
    """Constructs the graph and table visuals"""
    if graph == 'bar' and library.lower() == 'rocrand':
        fig, table = make_bar_plot(dataframe, title, extras, "AvgTime(1 trial)-ms")
        return fig, None
    if library.lower() == 'rocblas':
        fig, table = make_blas_visuals(dataframe, title, graph, versions, speedup_options)
        return fig, table
    speedup_dataframe = pd.DataFrame()
    df = dataframe
    df['xlength'] = df['xlength'].astype(str)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if graph == 'line':
        mode = 'lines'
    else:
        mode = 'lines+markers'
    mask = df['collection'].unique()
    dfs = [df[df['collection']== collection] for collection in mask]
    for df in dfs:
        name = df.iloc[0]['collection']
        name = rename(name)
        fig.add_trace(go.Scatter(x=df['xlength'], y=df['median'],
                    mode=mode,
                    name=name),
                    secondary_y=False)                            
    if len(list(set(speedup_options) & set(versions))) > 1:
        speedup_options = [value for value in speedup_options if value in versions]
        speedup_options.sort()
        options_collections = []
        for version in speedup_options:
            for collection in mask:
                if version in collection:
                    options_collections.append(collection)
        firstelement = speedup_options[0]
        # collections = mask
        collections = options_collections
        first_collections = [collection for collection in collections if firstelement in collection]
        first_collection = first_collections[0]
        del first_collections[0]
        reference_df =  dataframe[dataframe['collection']== first_collection]
        ref_name = rename(first_collection)
        speedup_dataframe['problem-size'] = reference_df['xlength']
        speedup_dataframe[f'median {ref_name}'] = reference_df['median']
        collections = [collection for collection in collections if collection != first_collection]

        for option in collections:
            opt_name = rename(option)
            option_df = dataframe[dataframe['collection']== option]
            speedup_dataframe[f'median {opt_name}'] = option_df['median']
        for option in collections:
            opt_name = rename(option)
            option_df = dataframe[dataframe['collection']== option]
            median_a = reference_df['median']
            median_b = option_df['median']
            speedup = median_a.subtract(median_b)
            speedup_dataframe[f'{opt_name} over {ref_name}'] = speedup
            ylist = speedup.tolist()

            fig.add_trace(
                go.Scatter(x=option_df['xlength'], y=ylist, name=opt_name + ' speedup over ' +
                ref_name),
                secondary_y=True,
            )


    fig.update_layout(title=title, height=700, font=dict(
        family="Courier New, monospace",
        size=12,
        color="RebeccaPurple"
    ), hovermode='x unified')
    fig.update_xaxes(title_text="Problem Size")
    fig.update_yaxes(title_text="Median Time (logarithmic)", type="log", secondary_y=False)
    fig.update_yaxes(title_text="Speedup", secondary_y=True)

    table = make_fft_table(speedup_dataframe)
    if len(list(set(speedup_options) & set(versions))) > 1:
        return fig, table
    else:
        return fig, None

def rename(collection):
    """Returns shorter name for the collection"""
    name = collection.split('/')
    rename_part1 = name[0].strip('gpu-')[0] + name[0].strip('gpu-')[-1] + '/'
    rename_part2 = name[2].strip('rocm')
    rename_part3 = name[3].split('-')
    rename_part3 = ''.join([i[0] for i in rename_part3])
    renamed = rename_part1 + rename_part2 + rename_part3
    return renamed.upper()


def make_fft_table(df):
    """Return the speedup table for fft. For the speedup
    columns, formating is done to show the divergent from the
    midpoint.
    """
    columns = list(df.columns)
    interest_cols = [i for i in columns if 'over' in i]
    style_data_conditional = [data_bars_diverging(df, a) for a in interest_cols]
    styles = [item for sublist in style_data_conditional for item in sublist]
    table = dash_table.DataTable(
        data=df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i, "type": 'numeric',
              "format": Format(precision=6, scheme=Scheme.fixed)} for i in df.columns],
        style_data_conditional=(
            styles
        ),
        style_cell={'minWidth': 105, 'maxWidth': 105, 'width': 105},
        style_header={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
    }

    )
    return table

def make_bar_plot(dataframe, title, extras, y_axis):
    """Make bar plot for rand for all selected algorithms"""
    df = dataframe
    df['group'] = df.apply(lambda row: ''.join(row.Algorithm.split('@')[1:]), axis = 1)
    interest_algos = []
    df_algos = df['Algorithm'].unique()
    for algo in extras:
        for df_algo in df_algos:
            if algo in df_algo:
                interest_algos.append(df_algo)
    dfs = [df[df['Algorithm']== algo] for algo in interest_algos]
    df = pd.concat(dfs)
    fig = px.bar(df, x="Algorithm", y=y_axis,
                 color="group", height=800,
                 hover_data=['Size', 'Samples-GSample/s'], text=y_axis)
    fig.update_layout(title=title, height=800, font=dict(
        family="Courier New, monospace",
        size=14,
        color="RebeccaPurple"
    ), showlegend=False)
    return fig, None

def add_rand_slider(plot_table, id_index):
    """Adds slider to select plots for Average time or
    Throughtput.
    """
    slider = dbc.Col(dcc.Slider(
        id= {'type':'rand-slider', 'index': id_index},
        min=0,
        max=1,
        step=None,
        marks={
            0: {'label':'Avg Time', 'style': {'color': '#f50'}},
            1: {'label':'Throughput', 'style': {'color': '#f50'}}
        },
        value=0
        ), xs=6, md=3, align='start', className='slider')
    plot_table = [*plot_table, slider]
    return plot_table

def make_rand_slider_plot(slide_num, frame, algos):
    """Returns new plot figure for selected y_axis.
    Calls the make_bar function with the specified y_axis value.
    """
    if slide_num == 0:
        y_axis = 'AvgTime(1 trial)-ms'
    else:
        y_axis = 'Throughput-GB/s'
    figure, _ = make_bar_plot(frame, "Performance Plot", algos, y_axis)
    return figure

def make_blas_visuals(dataframe, title, graph, _, __, sample=None):
    """Returns figure and table for blas test suites"""
    platform_dfs = get_suite_frames(dataframe)
    sampled_dfs, sample = sample_dataframes(platform_dfs, sample)
    df = pd.concat(sampled_dfs)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if graph == 'line':
        mode = 'lines'
    else:
        mode = 'lines+markers'
    mask = df['collection'].unique()
    dfs = [df[df['collection']== collection] for collection in mask]
    for df in dfs:
        name = df['collection'].unique()[0]   
        name = rename(name)
        fig.add_trace(go.Scatter(x=df['problem'], y=df['rocblas-Gflops'],
                    mode=mode,
                    name=name
                    ),
                    secondary_y=False)
    fig.update_layout(title=title, height=700, font=dict(
        family="Courier New, monospace",
        size=12,
        color="RebeccaPurple"
    ), hovermode='x unified')
    fig.update_xaxes(title_text="Problem number")
    fig.update_yaxes(title_text="rocblas-Gflops (logarithmic)", secondary_y=False, type='log')
    table = make_blas_table(dfs[0])
    return fig, table

def get_suite_frames(dataframe):
    """Returns individual dataframe for the collections selected
    so that individual plots would be made for them.
    This is generated from the concatenated dataframe passed to it
    """
    df = dataframe
    mask = df['collection'].unique()
    dfs = [df[df['collection']== collection] for collection in mask]
    return dfs

def sample_dataframes(ls_of_dfs, sample_pt):
    df = ls_of_dfs
    sliced_df = []
    i = sample_pt
    if i is None:
        i = 0
    for df in ls_of_dfs:
        df = copy.deepcopy(df)
        df.loc[:,'rocblas-Gflops'] = df.loc[:,'rocblas-Gflops'].astype(float)
        df['problem'] = str(i)
        sliced = df.iloc[i:i+108, :]
        sliced = copy.deepcopy(sliced)
        for j in range(i, i+108):
            sliced.loc[j,'problem'] = str(j)
        sliced_df.append(sliced)
    return sliced_df, j

def add_blas_slider(plot_table, id_index):
    """Add slider to plot that allows for sampling the blas
    suite data (slicing into two halves) as a single plot would be too much to look at.
    """
    slider = dbc.Col(dcc.Slider(
        id= {'type':'blas-slider', 'index': id_index},
        min=0,
        max=1,
        step=None,
        marks={
            0: {'label':'NN/NT', 'style': {'color': '#f50'}},
            1: {'label':'TN/TT', 'style': {'color': '#f50'}}
        },
        value=0
        ), xs=6, md=3, align='start', className='slider')
    plot_table = [*plot_table, slider]
    return plot_table

def make_blas_slider_plot(slide_num, blas_dataframe, blas_graph, blas_versions, blas_speedup_options):
    """Make plot for selected sampling point for blas. Calls the
    make_blas_visuals function for the visuals and returns it for plotting.
    """
    if slide_num == 0:
        sample_pt = 0
    else:
        sample_pt = 108
    figure, table = make_blas_visuals(blas_dataframe, "Performance Plot",
           blas_graph, blas_versions, blas_speedup_options, sample_pt)
    return figure, table

def make_blas_table(df):
    """Makes table specifying the problem being plotted for blas data suit"""
    df_p = df[['problem','transA','transB','M','N',
           'K','alpha','lda','beta','ldb','ldc','ldd','batch_count']]
    non_numeric = [{'name': i, 'id': i} for i in list(df_p.columns)[:3]]
    numeric = [{'name': i, 'id': i, "type": 'numeric',
         "format": Format(precision=6, scheme=Scheme.fixed)} for i in list(df_p.columns)[3:]]
    columns= non_numeric + numeric
    table = dash_table.DataTable(
        data=df_p.to_dict('records'),
        sort_action='native',
        columns=columns,
        fixed_rows={'headers': True},
        style_table={'height': '500px', 'overflowY': 'auto'}
    )
    return table

#Dynamic layout components below.

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

def generate_field_pair(num_clicks, selected_library):
    library = selected_library
    options = model.get_field_types(library)
    options = [{'label': item, 'value': item} for item in options]
    field_pair = html.Div(html.Div(id={'type': 'field-dropdown', 'index': num_clicks}, children=[
        html.Button('x', id={'type': 'self-remove', 'index': num_clicks}, className='self-remove-button', n_clicks=0),
        html.Div(dcc.Dropdown(
            id={'type': 'field-type-dropdown', 'index': num_clicks},
            options=options,
            placeholder='Field Type',
            className='pair-type-dropdown',
            style={'border-color': 'dodgerblue'}
        ), id='type-dropdown'),
        dcc.Dropdown(
            id={'type':'field-value-dropdown', 'index': num_clicks},
            options=[{'label':'Select Type', 'value':'Select Type', 'disabled':True, 'title': 'Select field type first'}],
            placeholder='Field Value',
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