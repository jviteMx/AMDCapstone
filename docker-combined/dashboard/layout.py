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