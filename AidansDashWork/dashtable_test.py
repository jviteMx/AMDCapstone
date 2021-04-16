import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input
from plotly.subplots import make_subplots
import pandas as pd
import model

def convert_tuple_to_df(tuple):
    return tuple[1]

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

# list of column names
# columns_names = [" ", " ", " ", " ", " ", " ", " "]
columns_names = ['dimension', 'xlength', 'mean of 3.6', 'mean of 3.8', 'mean of 3.9', 'speedup 3.8', 'speedup 3.9']

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
        
        html.Br(),
        html.Br(),

        # potential loadable column names template
        # https://dash.plotly.com/datatable/editable
        # html.Div(
        #     dash_table.DataTable(
        #         id='updateable-table',
        #         columns=[{
        #             'name': 'Column {}'.format(i),
        #             'id': 'column-{}'.format(i)
        #         } for i in range(1,10)],
        #         data=[
        #             {'column-{}'.format(i):
        #             (0) for i in range (1,10)}
        #             for j in range(10)
                
        #         ]

        #     )
        
        # )  
        
          html.Div(
            children=[
                html.Div(children="Data Table", className="Table" ),
                dash_table.DataTable(
                    id='updateable-table',
                    columns=[{'name': i, 'id': i} for i in columns_names],
                    style_cell={
                            'minWidth':95, 'maxWidth':95, 'width':95,
                            'textAlign': 'left'
                    },
                    # changes the cell size
                    style_data={
                        'whiteSpace': 'normal',
                        'minWidth': '40px', 'width': '180px', 'maxWidth': '180px',
                        'hieght': 'auto',
                        'width' : 'auto'
                    }
                    )
                    
            ],
            className='Wrapper'   
        
        )
    ]
)  

@app.callback(
        Output("updateable-table", 'data'),    
    [
        Input("platform-filter", "value"),
        Input("dataset-filter", "value"),
        Input("version-filter", "value"),
        Input("graph-filter", "value"),
        Input("speedup-filter", "value")
    ],
)
def update_charts(platform, dataset, versions, graph, speedup_options):
    # if platform == "GPU Server 1":
    #     platform = 'Spec1'


    # print(platform, dataset)
    filtered_data = model.get_concat_dataframe(platform, dataset, versions)
    if filtered_data.empty:
        return dash.no_update
    else:
    
        table = make_table(filtered_data, dataset, versions, graph, speedup_options)
        return  table



def make_table(dataframe, dataset, versions, graph, speedup_options):

    df = dataframe
    
    # print (versions)
    # options
    # 1. leave with if statements what what version is selected
    # 2. always create the three version dataframes and filter out if they are empty, ie empty means they werent selected for the query
    # 3. ????? open to sugesstions
   
    list_of_dropped_headers= ['dimension', 'xlength', 'nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median']

    # if 'ALL' is selected
    if 'All' in versions or '3.6' in versions and '3.9' in versions and '3.8' in versions:
        print("all/all three versions were selected")
        
        dff_36, dff_38, dff_39 = df.groupby(df['rocm version'])
        df_36 = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = temp_df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median'], axis=1)

        df_36['mean of 3.6'] = df_36['mean']
        # df_36['median of 3.6'] = df_36['median']
        df_36 = df_36.drop(list_of_dropped_headers, axis=1)

        df_38 = pd.DataFrame(convert_tuple_to_df(dff_38))
        df_38['mean of 3.8'] = df_38['mean']
        # df_38['median of 3.8'] = df_38['median']
        df_38 = df_38.drop(list_of_dropped_headers, axis=1)

        df_39 = pd.DataFrame(convert_tuple_to_df(dff_39))
        df_39['mean of 3.9'] = df_39['mean']
        # df_39['median of 3.9'] = df_39['median']
        df_39 = df_39.drop(list_of_dropped_headers, axis=1)    

        table_df = pd.concat([temp_df, df_36, df_38, df_39], axis=1)
        table_df['speedup 3.8'] = table_df['mean of 3.8'] - table_df['mean of 3.6']
        table_df['speedup 3.9'] = table_df['mean of 3.9'] - table_df['mean of 3.6']

        # table = dash_table.DataTable(id='updateable-table', data)
        # return[ {'Column {}'.format(i): (table_df.columns) for i in len(table_df.columns),
        #         'column-{}'.format(i): table_df for i in len(table_df.columns)}
        #         for j in range (len(table_df))
        #         ]
        # print(table_df.to_dict('records'))
        # print(table_df)
        return table_df.to_dict('records')

    elif '3.6' in versions and '3.8' in versions:  
        print('3.6 and 3.8 were selected')
        
        dff_36, dff_38 = df.groupby(df['rocm version'])
        df_36 = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = temp_df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median'], axis=1)

        df_36['mean of 3.6'] = df_36['mean']
        # df_36['median of 3.6'] = df_36['median']
        df_36 = df_36.drop(list_of_dropped_headers, axis=1)

        df_38 = pd.DataFrame(convert_tuple_to_df(dff_38))
        df_38['mean of 3.8'] = df_38['mean']
        # df_38['median of 3.8'] = df_38['median']
        df_38 = df_38.drop(list_of_dropped_headers, axis=1)
    

        table_df = pd.concat([temp_df, df_36, df_38], axis=1)
        table_df['speedup 3.8'] = table_df['mean of 3.8'] - table_df['mean of 3.6']
        

        return table_df.to_dict('records')
        
    elif '3.6' in versions and '3.9' in versions:
        print('3.6 and 3.9 were selected')
        dff_36, dff_39 = df.groupby(df['rocm version'])
        df_36 = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = pd.DataFrame(convert_tuple_to_df(dff_36))
        temp_df = temp_df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median'], axis=1)

        df_36['mean of 3.6'] = df_36['mean']
        # df_36['median of 3.6'] = df_36['median']
        df_36 = df_36.drop(list_of_dropped_headers, axis=1)

        df_39 = pd.DataFrame(convert_tuple_to_df(dff_39))
        df_39['mean of 3.9'] = df_39['mean']
        # df_39['median of 3.9'] = df_39['median']
        df_39 = df_39.drop(list_of_dropped_headers, axis=1)    

        table_df = pd.concat([temp_df, df_36, df_39], axis=1)
        
        table_df['speedup 3.9'] = table_df['mean of 3.9'] - table_df['mean of 3.6']
        return table_df.to_dict('records')

    elif '3.8' in versions and '3.9' in versions:
        print('3.8 and 3.9 were selected')
        
        dff_38, dff_39 = df.groupby(df['rocm version'])
        df_38 = pd.DataFrame(convert_tuple_to_df(dff_38))
        temp_df = pd.DataFrame(convert_tuple_to_df(dff_38))
        temp_df = temp_df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'mean', 'median'], axis=1)

       
        df_38['mean of 3.8'] = df_38['mean']
        # df_38['median of 3.8'] = df_38['median']
        df_38 = df_38.drop(list_of_dropped_headers, axis=1)

        df_39 = pd.DataFrame(convert_tuple_to_df(dff_39))
        df_39['mean of 3.9'] = df_39['mean']
        # df_39['median of 3.9'] = df_39['median']
        df_39 = df_39.drop(list_of_dropped_headers, axis=1)    

        table_df = pd.concat([temp_df, df_38, df_39], axis=1)
    
        return table_df.to_dict('records')

    # if only one version is selected
    elif '3.6' in versions or '3.8' in versions or '3.9' in versions:
        print('only one version selected')
        
        
        df = df.drop(['nbatch', 'nsample', 'samples', 'rocm version', 'median'], axis=1)

        if versions[0] == '3.6':
            df['mean of 3.6'] = df['mean']
            df = df.drop('mean', axis=1)
            return df.to_dict('records')
            
        elif versions[0] == '3.8':
            df['mean of 3.8'] = df['mean']
            df = df.drop('mean', axis=1)
            return df.to_dict('records')

        elif versions[0] == '3.9':
            df['mean of 3.9'] = df['mean']
            df = df.drop('mean', axis=1)
            return df.to_dict('records')

        
   


    


    





if __name__ == "__main__":
    app.run_server(debug=True)    