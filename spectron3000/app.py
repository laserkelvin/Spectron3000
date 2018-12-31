
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.exceptions import PreventUpdate

from spectron3000 import classes
from spectron3000 import plotting


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        dcc.Store(id="stored-data", storage_type="session"),
        html.Div(
            [
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Spectrum File - Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '40%',
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
                        'width': '40%',
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
            ]
        ),
        html.Div(id='output-data-upload'),
        dcc.Graph(id="main-graph"),
        html.H4("Catalog Table"),
        dt.DataTable(
            editable=True,
            id='catalog-table'
        ),
    ]
)


@app.callback(Output("stored-data", "data"),
              [Input("upload-data", "contents"), Input("upload-data", "filename")],
              [State("stored-data", "data")]
              )
def upload_spectrum(uploaded_file, filename, data):
    """
    This creates a callback function for when a user uploads a spectrum.
    The data is stored in a hidden Dash div (`Store` object), which holds
    a dictionary that separates a spectrum from catalog files.
    :param uploaded_file: file stream from Dash `Upload`
    :param filename: str uploaded file name
    :param data: dict containing spectrum and catalog data
    :return: instance of `Spectrum` object
    """
    # Only update if a file is actually uploaded
    if uploaded_file is None:
        raise PreventUpdate
    spec_obj = classes.Spectrum.from_upload(uploaded_file, filename)
    # Since the same object is used to store both spectra and catalogs
    # we only want to update the spectrum
    data = data or {"spectrum": {}, "catalogs": {}}
    data["spectrum"]["x"] = spec_obj.df["Frequency (MHz)"]
    return data


@app.callback(Output("main-graph", "figure"),
              [Input("stored-data", "data")]
              )
def update_plot(data):
    """
    This callback is set up to track the hidden div data. When something
    changes from the user uploading a spectrum or catalog file, the main
    graph is updated with the latest data.
    :param data: dict from the hidden div Store
    :return: dict with plot specifications
    """
    spectrum = data["spectrum"].create_plot()
    plot_data = {
        "data": [spectrum],
        "layout": plotting.init_layout()
    }
    return plot_data


if __name__ == '__main__':
    app.run_server(debug=True)
