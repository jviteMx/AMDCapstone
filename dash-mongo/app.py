import dash
import dash_core_components as dcc
import dash_html_components as html
import model
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input


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
    ],
)
def update_charts(platform, dataset, versions, graph):
    filtered_data = model.get_concat_dataframe(platform, dataset, versions)
    if filtered_data.empty:
        return px.line()
    else: 
        figure = px.line(filtered_data, x="xlength", y="mean", color='version')

        return figure

if __name__ == "__main__":
    app.run_server(debug=True)    
