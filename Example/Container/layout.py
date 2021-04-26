# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi on LinkedIn

"""Make dash instance and generate the static initial components."""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import model
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                 suppress_callback_exceptions=True, prevent_initial_callbacks=True)
app.title = "Rocm Analytics: Analyze the performance of libraries"

app.layout = html.Div(
    id='layout',
    children=[
        dbc.Jumbotron(html.Div(
            children=[
                html.P(children=html.Div(html.Img(src=app.get_asset_url('amd.png')))),
                html.H1(
                    children=["MLSE Library Performance Monitor Notebook", html.Span('ish',
                    className='ish',contentEditable='true')], className="header-title"
                ),
                html.P(
                    children="Analyze the performance of rocm math libraries",
                    className="header-description",
                ),
            ],
            className="header",
        ), style={'background-color': '#262b2f'}, fluid=True),

        html.Div(dbc.Row(
            id='dynamic-header-menu-container',
            children=[
                html.Div(dcc.Dropdown(
                    id='libraries-dropdown',
                    options=[{'label': i, 'value': i} for i in model.get_registered_libraries()],
                    placeholder='Select Library',
                    clearable=False,
                    className='library-dropdown'
                ), id='library-id'),
            ],
            no_gutters=True
        ),className='dynamic-header-menu-container1'),

        html.Div(id={'type':'dynamic-menu-output-container', 'index':1},
                 children=[], className='menu-rows-container'),
        html.Div(id='intermediate-library-value', style={'display': 'none'}) # Sharing selected library between callbacks | strategy to avoid global variables by storing data
                                                                             #in user brower section
    ]
)