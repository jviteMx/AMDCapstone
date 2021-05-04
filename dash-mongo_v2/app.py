import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input
from plotly.subplots import make_subplots
import model
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
                    children="ROCm Analytics", className="header-title"
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
                        html.Div(children="Platform", className="menu-title"),
                        dcc.Dropdown(
                            id="platform-filter",
                            options=[
                                # {"label": platform, "value": platform}
                                # for platform in registered_platforms
                                {"label": 'Spec1', "value": 'Spec1'},
                                {"label": 'Spec2', "value": 'Spec2', "disabled": True},
                            ],
                            value="Spec1",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Data-group", className="menu-title"),
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
                        html.Div(children="Version(s)", className="menu-title"),
                        dcc.Dropdown(
                            id="version-filter",
                            options=[
                                {"label": version, "value": version}
                                for version in registered_libraries
                            ],
                            value=registered_libraries[-1:],
                            clearable=False,
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
                            clearable=False,
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
    ]
)  

@app.callback(
    Output("chart", "figure"),
    [
        Input("platform-filter", "value"),
        Input("dataset-filter", "value"),
        Input("version-filter", "value"),
        Input("graph-filter", "value"),
        Input("speedup-filter", "value")
    ],
)
def update_charts(platform, dataset, versions, graph, speedup_options):
    filtered_data = model.get_concat_dataframe(platform, dataset, versions)
    if filtered_data.empty:
        return px.line()
    else:
        fig = make_graph(filtered_data, dataset, graph, versions, speedup_options)
        return fig

def make_graph(dataframe, title, graph, versions, speedup_options):
    df = dataframe
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    mode = ''
    if graph == 'line':
        mode = 'lines'
    else:
        mode = 'lines+markers'    
    mask = df['rocm version'].unique()
    dfs = [df[df['rocm version']== version] for version in mask]
    for df in dfs:
        fig.add_trace(go.Scatter(x=df['xlength'], y=df['median'],
                    mode=mode,
                    name='rocm' + df.iloc[0]['rocm version']),
                    secondary_y=False,)            
    if len(speedup_options) > 1 and (len(versions) > 1) and ('All' not in versions) and len(list(set(speedup_options) & set(versions))) > 1:
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
                go.Scatter(x=option_df['xlength'], y=ylist, name='rocm' + option + ' speedup over ' + 
                'rocm' + speedup_options[0]),
                secondary_y=True,
            )


    fig.update_layout(title=title, height=800, font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    ))
    fig.update_xaxes(title_text="problem size (logarithmic)", type="log") 
    fig.update_yaxes(title_text="Median Time (logarithmic)", type="log", secondary_y=False)
    fig.update_yaxes(title_text="Speedup", secondary_y=True)                                #rangemode="nonnegative"  range=[-2,2]
    return fig 

if __name__ == "__main__":
    app.run_server(debug=True)    