# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from dash_table.Format import Format, Align, Scheme
from plotly.subplots import make_subplots
import model
import pandas as pd

def convert_tuple_to_df(tuple):
    return tuple[1]
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

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
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ), 
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        # location for the dash table
        html.Div(
            children=[
                # html.Label("Data Table"),
                html.Div(id='table1'),
            ],
            className="table"
        ),
        html.Br()
    ]
)  

@app.callback( 
    [ Output("chart", "figure"), Output("table1", 'children')],   
    [ Input("platform-filter", "value"),Input("dataset-filter", "value"),Input("version-filter", "value"),
        Input("graph-filter", "value"),Input("speedup-filter", "value")],
    State("speedup-filter", "value"),
    
)
def update_charts(platform, dataset, versions, graph, speedup_options, value):
    # if platform == "GPU Server 1":
    #     platform = 'Spec1'
    filtered_data = model.get_concat_dataframe(platform, dataset, versions)
    if filtered_data.empty:
        raise PreventUpdate
    else:
        # call for the graph
        fig = make_graph(filtered_data, dataset, graph, versions, speedup_options)

        # call for the table
        df = make_dataframe(filtered_data, dataset, versions, graph, speedup_options)
        data = df.to_dict('records')
        columns =  [{"name": i, "id": i } 
        if i == "dimension" or i =="xlength"
        # precision makes the data round to a decimal, scheme.fixed holds all numbers to be uniform by adding 0 to the end
        else {"name": i, "id": i, "type": 'numeric', "format": Format(precision =6, scheme= Scheme.fixed) }
        
        for i in (df.columns)]

        if 'speedup 3.8' in df.columns and 'speedup 3.9' in df.columns:
            # styles = discrete_background_color_bins(df,columns=['speedup 3.8','speedup 3.9'])
            return fig, dash_table.DataTable(data=data,
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
            return fig, dash_table.DataTable(data=data, columns=columns,
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
            return  fig, dash_table.DataTable(data=data, columns=columns,
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

        return fig, dash_table.DataTable(data=data, columns=columns, style_data_conditional=([
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

def make_graph(dataframe, title, graph, versions, speedup_options):
    df = dataframe
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    mode = ''
    if graph == 'line':
        mode = 'lines'
    else:
        mode = 'lines+markers'    
    mask = df['rocm version'].unique()
    # print(mask[0])
    # print(df)
    dfs = [df[df['rocm version']== version] for version in mask]
    for df in dfs:
        fig.add_trace(go.Scatter(x=df['xlength'], y=df['median'],
                    mode=mode,
                    name='ROCm' + df.iloc[0]['rocm version']),
                    secondary_y=False,)            
    if len(list(set(speedup_options) & set(versions))) > 1:         #len(speedup_options) > 1 and (len(versions) > 1) and ('All' not in versions) and 
        speedup_options = [value for value in speedup_options if value in versions]
        speedup_options.sort()
        
        firstelement = speedup_options[0] 
        reference_df =  dataframe[dataframe['rocm version']== firstelement]                
        for option in speedup_options[1:]:
            option_df = dataframe[dataframe['rocm version']== option]
            median_a = reference_df['median']
            median_b = option_df['median']
            opt_df = median_a.subtract(median_b)
            ylist = opt_df.tolist()

            fig.add_trace(
                go.Scatter(x=option_df['xlength'], y=ylist, name='ROCm' + option + ' speedup over ' + 
                'ROCm' + speedup_options[0]),
                secondary_y=True,
            )
    fig.update_layout(title=title, height=700, font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    ))
    fig.update_xaxes(title_text="Problem Size (logarithmic)", type="log") 
    fig.update_yaxes(title_text="Median Time (logarithmic)", type="log", secondary_y=False)
    fig.update_yaxes(title_text="Speedup", secondary_y=True)                                #rangemode="nonnegative"  range=[-2,2]
    return fig

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
        df_36['mean of 3.6'] = df_36['mean'].round(5)
        df_36 = df_36.drop(list_of_dropped_headers, axis=1)
        df_38 = pd.DataFrame(convert_tuple_to_df(dff_38))
        df_38['mean of 3.8'] = df_38['mean'].round(5)
        df_38 = df_38.drop(list_of_dropped_headers, axis=1)
        df_39 = pd.DataFrame(convert_tuple_to_df(dff_39))
        df_39['mean of 3.9'] = df_39['mean'].round(5)
        df_39 = df_39.drop(list_of_dropped_headers, axis=1)    
        table_df = pd.concat([temp_df, df_36, df_38, df_39], axis=1)

        table_df['speedup 3.8'] = table_df['mean of 3.8'] - table_df['mean of 3.6']
        table_df['speedup 3.8'] = table_df['speedup 3.8'].append(lambda x :'⬇️ '  if x < 0 else '⬆️ ')
        # for item in table_df['speedup 3.8']:
        #     if item < 0:
        #         item =  "⬇️ " + item
        #     else:
        #         item = "⬆️ " + item

        table_df['speedup 3.9'] = table_df['mean of 3.9'] - table_df['mean of 3.6']
        table_df['speedup 3.9'] = table_df['speedup 3.9'].apply(lambda x:'⬇️ ' if x < 0 else '⬆️ ')
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
        table_df['speedup 3.9'] = table_df['speedup 3.9']
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

if __name__ == "__main__":
    app.run_server(debug=True)    