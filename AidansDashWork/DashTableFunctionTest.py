import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
from plotly.subplots import make_subplots
from dash.exceptions import PreventUpdate
import seaborn as sns
import pandas as pd
import numpy as np
import model
import colorlover
from dash_table.Format import Format, Align, Scheme
import dash_table.FormatTemplate as FormatTemplate

def convert_tuple_to_df(tuple):
    return tuple[1]

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


def discrete_background_color_bins(df, n_bins=9, columns='all'):
    
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    # print('bounds')
    # print(bounds)
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
        # print('df_numeric_columns')
        # print(df_numeric_columns)
    df_max = df_numeric_columns.max().max() # max number from the columns
    # print('max')
    # print(df_max)
    df_min = df_numeric_columns.min().min() # in number from the columns

    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    # print('ranges')
    # print(ranges)
    styles = []
    
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        
        backgroundColor = colorlover.scales[str(n_bins)]['seq']['Blues'][i -1]
        color = 'white' if i > len(bounds) / 2. else 'inherit'

        # for column in df_numeric_columns:
        #     styles.append({
        #         'if': {
        #             'filter_query': (
        #                 '{{{column}}} >= {min_bound}' +
        #                 (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
        #             ).format(column=column, min_bound=min_bound, max_bound=max_bound),
        #             'column_id': column
        #         },
        #         'backgroundColor': backgroundColor,
        #         'color': color
        #     })
        # print(df_numeric_columns)
        for column in df_numeric_columns:
            print(column)
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} > 0' 
                        ).format(column=column),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            }
            )
            # styles.append({
                
            #   'if': {
            #         'filter_query': (
            #             '{{{column}}} >= 0.1 ' + (' && {{{column}}} < 0.5') 
            #             ).format(column=column),
            #         'column_id': column
            #     },
            #     'backgroundColor': "lightgreen",
            #     'color': 'white'  
            
            # })
        print(styles)
    return styles
# {
#                  "if": {
#                      "column_id": 'speedup 3.8',

#                      "filter_query": ('{speedup 3.8} > 0.6').format(column=column),
#                  },
#                  "background color":  "lime",
#              },
#              {
#                  "if": {
#                      "column_id": 'speedup 3.8',

#                      "filter_query": '{speedup 3.8} >= 0.1 && {speedup 3.8} < 0.5',
#                  },
#                  "background color" : "lightgreen"
#              },
#              {
#                  "if": {
#                      "column_id": 'speedup 3.8',

#                      "filter_query": '{speedup 3.8} < -0.1 && {speedup 3.8} >= -0.5',
#                  },
#                  "background color" : "indianred"
#              },
#              {
#                  "if": {
#                      "column_id": 'speedup 3.8',

#                      "filter_query": '{speedup 3.8} < -0.6',
#                  },
#                  "background color" : "darkred"
#              }



#Get registered data from the model module
registered_platforms = model.registered_platforms
registered_data_groups = model.registered_data_groups
registered_libraries = model.registered_libraries.tolist()
speedup_option = model.registered_libraries.tolist()
registered_libraries.append('All')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Rocm Analytics: Analyze the performance of libraries"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="AMD", className="header-emoji"),
                html.H1(
                    children="FFT ROCm Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the performance of rocm libraries"
                    " from version 3.6",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Hardware ID", className="menu-title"),
                        dcc.Dropdown(
                            id="platform-filter",
                            options=[
                                # {"label": platform, "value": platform}
                                # for platform in registered_platforms
                                {"label": 'GPU Server 1', "value": 'Spec1'},
                                {"label": 'GPU Server2', "value": 'Spec2', "disabled": True},
                            ],
                            value="Spec1",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Test-Suite", className="menu-title"),
                        dcc.Dropdown(
                            id="dataset-filter",
                            options=[
                                {"label": data_group, "value": data_group}
                                for data_group in registered_data_groups
                            ],
                            value="R2-D1-C2C-IP",
                            clearable=False,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="ROCm Version(s)", className="menu-title"),
                        dcc.Dropdown(
                            id="version-filter",
                            options=[
                                {"label": version, "value": version}
                                for version in registered_libraries
                            ],
                            value=registered_libraries[-1:],
                            #clearable=False,
                            searchable=True,
                            multi=True,
                            className="dropdown",
                        ),
                    ],
                ), 
                html.Div(
                    children=[
                        html.Div(children="Graph", className="menu-title"),
                        dcc.Dropdown(
                            id="graph-filter",
                            options=[
                                {"label": graph, "value": graph}
                                for graph in ['line', 'marker-line']
                            ],
                            value="line",
                            clearable=False,
                            searchable=True,
                            className="dropdown",
                        ),
                    ],
                ), 
                html.Div(
                    children=[
                        html.Div(children="Speedup Option", className="menu-title"),
                        dcc.Dropdown(
                            id="speedup-filter",
                            options=[
                                {"label": version, "value": version}
                                for version in speedup_option
                            ],
                            value=speedup_option[-2:],
                            #clearable=False,
                            searchable=True,
                            multi=True,
                            className="dropdown",
                        ),
                    ],
                ),                                              
            ],
            className="menu",
        ),   
        html.Div(
            dcc.ConfirmDialog(
                id="error_message",
                message="one or more version files are missing for this test"
            )
        ),
        html.Br(),
        html.Br(),

        html.Div(
            children=[
                
                # html.Button('speedup', id="speedup_button", type = 'text'),
                html.Div(id='table1'),
            ],
            className="table"
            
        )
    ],
    
)  

@app.callback(
        Output("table1", "children"), 

    [   Input("platform-filter", "value"),
        Input("dataset-filter", "value"),
        Input("version-filter", "value"),
        Input("graph-filter", "value"),
        Input("speedup-filter", "value")
    ],

        State("speedup-filter", "value"),
    
)






def update_charts(platform, dataset, versions, graph, speedup_options, value):
    
    filtered_data = model.get_concat_dataframe(platform, dataset, versions)
    if filtered_data.empty:
        raise PreventUpdate
    else:
        df = make_dataframe(filtered_data, dataset, versions, graph, speedup_options)
        data = df.to_dict('records')
        columns =  [{"name": i, "id": i } 
        if i == "dimension" or i =="xlength"
        # precision makes the data round to a decimal, scheme.fixed holds all numbers to be uniform by adding 0 to the end
        else {"name": i, "id": i, "type": 'numeric', "format": Format(precision =6, scheme= Scheme.fixed) }
        
        for i in (df.columns)] 


        
        if 'speedup 3.8' in df.columns and 'speedup 3.9' in df.columns:
            # styles = discrete_background_color_bins(df,columns=['speedup 3.8','speedup 3.9'])
            return  dash_table.DataTable(data=data,
             columns=columns,
             style_data_conditional=([
                 {'if': { 'filter_query': '{speedup 3.8} >= 0','column_id': 'speedup 3.8'},
                     'backgroundcolor': 'lime',
                     'color': 'lime'},
                 {'if': {'filter_query': '{speedup 3.8} < 0','column_id': 'speedup 3.8'},
                     'backgroundcolor': 'red',
                     'color': 'red'},
                 {'if': {'filter_query': '{speedup 3.9} >= 0','column_id': 'speedup 3.9'},
                     'color': 'lime' },
                 {'if': {'filter_query': '{speedup 3.9} < 0','column_id': 'speedup 3.9'},
                     'color': 'red' }
             ])
             )

        elif 'speedup 3.8' in df.columns:
            styles = discrete_background_color_bins(df, columns=['speedup 3.8'])
            # (styles, legend) = discrete_background_color_bins(df, columns=['speedup 3.8'])
            return  dash_table.DataTable(data=data, columns=columns,
             style_data_conditional=([
                 {'if': { 'filter_query': '{speedup 3.8} >= 0','column_id': 'speedup 3.8'},
                     'backgroundcolor': 'lime',
                     'color': 'lime'},
                 {'if': {'filter_query': '{speedup 3.8} < 0','column_id': 'speedup 3.8'},
                     'backgroundcolor': 'red',
                     'color': 'red'},
                 {'if': {'filter_query': '{speedup 3.9} >= 0','column_id': 'speedup 3.9'},
                     'color': 'lime' },
                 {'if': {'filter_query': '{speedup 3.9} < 0','column_id': 'speedup 3.9'},
                     'color': 'red' }
             ]))

        elif 'speedup 3.9' in df.columns:
            styles = discrete_background_color_bins(df, columns=['speedup 3.9'])
            # (styles, legend) = discrete_background_color_bins(df, columns=['speedup 3.9'])
            return  dash_table.DataTable(data=data, columns=columns,
             style_data_conditional=([
                 {'if': { 'filter_query': '{speedup 3.8} >= 0','column_id': 'speedup 3.8'},
                     'backgroundcolor': 'lime',
                     'color': 'lime'},
                 {'if': {'filter_query': '{speedup 3.8} < 0','column_id': 'speedup 3.8'},
                     'backgroundcolor': 'red',
                     'color': 'red'},
                 {'if': {'filter_query': '{speedup 3.9} >= 0','column_id': 'speedup 3.9'},
                     'color': 'lime' },
                 {'if': {'filter_query': '{speedup 3.9} < 0','column_id': 'speedup 3.9'},
                     'color': 'red' }
             ]))

        # return  dash_table.DataTable(data=data, columns=columns, style_data_conditional=styles)
        return  dash_table.DataTable(data=data, columns=columns,
             style_data_conditional=([
                 {'if': { 'filter_query': '{speedup 3.8} >= 0','column_id': 'speedup 3.8'},
                     'backgroundcolor': 'lime',
                     'color': 'lime'},
                 {'if': {'filter_query': '{speedup 3.8} < 0','column_id': 'speedup 3.8'},
                     'backgroundcolor': 'red',
                     'color': 'red'},
                 {'if': {'filter_query': '{speedup 3.9} >= 0','column_id': 'speedup 3.9'},
                     'color': 'lime' },
                 {'if': {'filter_query': '{speedup 3.9} < 0','column_id': 'speedup 3.9'},
                     'color': 'red' }
             ]))     
                
             


def make_dataframe(dataframe, dataset, versions, graph, speedup_options):
    df = dataframe

    

    list_of_dropped_headers= ['dimension', 'xlength', 'nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median']
    # if 'ALL' is selected
    if 'All' in versions or '3.6' in versions and '3.9' in versions and '3.8' in versions:
        # print("all/all three versions were selected")
        dff_36, dff_38, dff_39 = df.groupby(df['rocm version'])
        df_36 = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = temp_df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median'], axis=1)
        df_36['mean of 3.6'] = df_36['mean']
        df_36 = df_36.drop(list_of_dropped_headers, axis=1)
        df_38 = pd.DataFrame(convert_tuple_to_df(dff_38))
        df_38['mean of 3.8'] = df_38['mean']
        df_38 = df_38.drop(list_of_dropped_headers, axis=1)
        df_39 = pd.DataFrame(convert_tuple_to_df(dff_39))
        df_39['mean of 3.9'] = df_39['mean']
        df_39 = df_39.drop(list_of_dropped_headers, axis=1) 

        table_df = pd.concat([temp_df, df_36, df_38, df_39], axis=1)

        

        table_df['speedup 3.8'] = table_df['mean of 3.8'] - table_df['mean of 3.6']
        table_df['speedup 3.9'] = table_df['mean of 3.9'] - table_df['mean of 3.6']
       
        

        return table_df

    elif '3.6' in versions and '3.8' in versions:  
        dff_36, dff_38 = df.groupby(df['rocm version'])
        df_36 = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = temp_df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median'], axis=1)
        df_36['mean of 3.6'] = df_36['mean']
        df_36 = df_36.drop(list_of_dropped_headers, axis=1)
        df_38 = pd.DataFrame(convert_tuple_to_df(dff_38))
        df_38['mean of 3.8'] = df_38['mean']
        df_38 = df_38.drop(list_of_dropped_headers, axis=1)
        table_df = pd.concat([temp_df, df_36, df_38], axis=1)
        table_df['speedup 3.8'] = table_df['mean of 3.8'] - table_df['mean of 3.6']
        
        return table_df
        
    elif '3.6' in versions and '3.9' in versions:
        dff_36, dff_39 = df.groupby(df['rocm version'])
        df_36 = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = temp_df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median'], axis=1)
        df_36['mean of 3.6'] = df_36['mean']
        df_36 = df_36.drop(list_of_dropped_headers, axis=1)
        df_39 = pd.DataFrame(convert_tuple_to_df(dff_39))
        df_39['mean of 3.9'] = df_39['mean']
        df_39 = df_39.drop(list_of_dropped_headers, axis=1)    
        table_df = pd.concat([temp_df, df_36, df_39], axis=1)
        table_df['speedup 3.9'] = table_df['mean of 3.9'] - table_df['mean of 3.6']
        return table_df

    elif '3.8' in versions and '3.9' in versions:
        dff_38, dff_39 = df.groupby(df['rocm version'])
        df_38 = pd.DataFrame(convert_tuple_to_df(dff_38))
        temp_df = pd.DataFrame(convert_tuple_to_df(dff_38))
        temp_df = temp_df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median'], axis=1)
        df_38['mean of 3.8'] = df_38['mean']
        df_38 = df_38.drop(list_of_dropped_headers, axis=1)
        df_39 = pd.DataFrame(convert_tuple_to_df(dff_39))
        df_39['mean of 3.9'] = df_39['mean']
        df_39 = df_39.drop(list_of_dropped_headers, axis=1)    
        table_df = pd.concat([temp_df, df_38, df_39], axis=1)
        return table_df

    # if only one version is selected
    elif '3.6' in versions or '3.8' in versions or '3.9' in versions:
        df = df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'median'], axis=1)
        if versions[0] == '3.6':
            df['mean of 3.6'] = df['mean']
            df = df.drop('mean', axis=1)
            return df
        elif versions[0] == '3.8':
            df['mean of 3.8'] = df['mean']
            df = df.drop('mean', axis=1)
            return df
        elif versions[0] == '3.9':
            df['mean of 3.9'] = df['mean']
            df = df.drop('mean', axis=1)
            return df

@app.callback(
    Output('error_message','exception'),

)




    





if __name__ == "__main__":
    app.run_server(debug=True)    