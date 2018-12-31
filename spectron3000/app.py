
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
        dcc.Store(id="plot-data", storage_type="session"),
        html.Div(
            [
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Spectrum File - Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '48%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    className="six columns"
                ),
                dcc.Upload(
                    id='upload-catalog',
                    children=html.Div([
                        'Catalog Files - Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '48%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=True,
                    className="six columns"
                ),
            ],
            className="row"
        ),
        html.Div(id='output-data-upload'),
        dcc.Graph(id="main-graph", style={"height": "600px", "title": "Main Plot"}),
        html.H4("Catalog Table", style={"text-align": "center"}),
        dt.DataTable(
            editable=True,
            columns=["Molecule", "Temperature (K)", "Column Density (cm^-2)", "Doppler (km/s)"],
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
    data["spectrum"] = spec_obj.__dict__
    return data


@app.callback(Output("stored-data", "data"),
              [Input("upload-catalog", "contents"), Input("upload-catalog", "filename")],
              [State("stored-data", "data")]
              )
def upload_catalog(uploaded_files, filenames, data):
    """
    This creates a callback function for when a user uploads one or multiple catalog files.
    The data is stored in a hidden Dash div (`Store` object), which holds
    a dictionary that separates a spectrum from catalog files.
    :param uploaded_files: list of file stream from Dash `Upload`
    :param filenames: list of str uploaded file name
    :param data: dict containing spectrum and catalog data
    :return: updated dictionary of data
    """
    # Only update if a file is actually uploaded
    if uploaded_file is None:
        raise PreventUpdate
    catalog_dict = {}
    for uploaded_file, filename in zip(uploaded_files, filenames):
        cat_obj = classes.Catalog.from_upload(uploaded_file, filename)
        catalog_dict[cat_obj.molecule] = cat_obj.__dict__
    # Since the same object is used to store both spectra and catalogs
    # we only want to update the spectrum
    data = data or {"spectrum": {}, "catalogs": {}}
    data["catalogs"].update(catalog_dict)
    return data


@app.callback(Output("main-graph", "figure"),
              [Input("stored-data", "data")]
              )
def update_figure(data):
    """
    This callback is set up to track the hidden div data. When something
    changes from the user uploading a spectrum or catalog file, the main
    graph is updated with the latest data.
    :param data: dict from the hidden div Store
    :return: dict with plot specifications
    """
    plots = list()
    spec_obj = classes.Spectrum(**data["spectrum"])
    # Create a Plotly Scatter trace
    plots.append(
        plotting.plot_spectrum(
            spec_obj.x,
            spec_obj.y,
            spec_obj.comment
        )
    )
    if len(data["catalogs"]) > 0:
        for molecule, cat_data in data["catalogs"].items():
            cat_obj = classes.Catalog(**cat_data)
            sim_y = cat_obj.generate_spectrum(
                spec_obj.x
            )
            plots.append(
                plotting.plot_spectrum(
                    spec_obj.x,
                    sim_y,
                    cat_obj.molecule
                )
            )
    plot_data = {
        "data": plots,
        "layout": plotting.init_layout()
    }
    return plot_data


@app.callback(
    Output("catalog-table", "data"),
    [Input("stored-data", "data")],
)
def update_table(data):
    """
    Callback for updating the DataTable, triggered by the stored-data
    changing whenever the user uploads a file.
    :param data:
    :return:
    """
    if len(data["catalogs"]) == 0:
        raise PreventUpdate
    cat_objs = [classes.Catalog(**catalog) for catalog in data["catalogs"].values()]
    table_data = [cat_obj.to_table_format() for cat_obj in cat_objs]
    return table_data

if __name__ == '__main__':
    app.run_server(debug=True)
