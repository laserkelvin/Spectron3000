
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import pandas as pd
import numpy as np

from . import classes


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        dcc.Store(id="stored-data", storage_type="session"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Spectrum File - Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '50%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
        ),
        dcc.Upload(
            id='upload-cat',
            children=html.Div([
                'Catalog Files - Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '50%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=True
        ),
        html.Div(id='output-data-upload'),
        html.H4('Catalog Table'),
        dt.DataTable(
            editable=True,
            id='catalog-table'
    ),
]
)

@app.callback(Output("output-data-upload", "children"),
              Input("upload-data", "contents"),
              Input("upload-data", "filename")
              )
def upload_spectrum(uploaded_file, filename):




if __name__ == '__main__':
    app.run_server(debug=True)