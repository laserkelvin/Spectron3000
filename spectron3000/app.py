
import numpy as np
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
                        "Drag and Drop or ",
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '98%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    className="six columns",
                    multiple=True
                )
            ],
            className="row"
        ),
        html.Div(id='output-data-upload'),
        dcc.Graph(id="main-graph", style={"height": "600px", "title": "Main Plot"}),
        html.H4("Catalog Table", style={"text-align": "center"}),
        dt.DataTable(
            editable=True,
            columns=[
                {"name": value, "id": value} for value in [
                    "molecule", "temperature", "column_density", "doppler"
                ]
            ],
            id='catalog-table'
        ),
    ]
)


@app.callback(Output("stored-data", "data"),
              [Input("upload-data", "contents"), Input("upload-data", "filename")],
              [State("stored-data", "data")]
              )
def upload_file(uploaded_files, filenames, data):
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
    if uploaded_files is None:
        raise PreventUpdate
    # In case there's no data yet, initialize with empty dicts
    data = data or {"spectrum": {}, "catalogs": {}}
    for uploaded_file, filename in zip(uploaded_files, filenames):
        # Check filename extension to determine which bin the data goes into
        upload_obj = classes.process_upload(uploaded_file, filename)
        # If the uploaded object returns a Spectrum, then assign it to spectrum
        if type(upload_obj) == classes.Spectrum:
            data["spectrum"] = upload_obj.__dict__
        else:
            data["catalogs"][upload_obj.molecule] = upload_obj.__dict__
    return data


@app.callback(Output("main-graph", "figure"),
              [
                  Input("stored-data", "data"),
                  Input("catalog-table", "derived_virtual_data"),
              ]
              )
def update_figure(data, table_data):
    """
    This callback is set up to track the hidden div data. When something
    changes from the user uploading a spectrum or catalog file, the main
    graph is updated with the latest data.
    :param data: dict from the hidden div Store
    :return: dict with plot specifications
    """
    plots = list()
    if data is None:
        raise PreventUpdate
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
            if table_data:
                table_dict = [
                    cat for cat in table_data if cat.get("molecule") == cat_data["molecule"]
                ][0]
                cat_data.update(table_dict)
            cat_data["frequency"] = np.array(cat_data["frequency"])
            cat_data["intensity"] = np.array(cat_data["intensity"])
            cat_data["state_energies"] = np.array(cat_data["state_energies"])
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
