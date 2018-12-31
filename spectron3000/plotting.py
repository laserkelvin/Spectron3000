
from plotly import graph_objs as go


def init_layout():
    layout = {
        "xaxis": {
            "title": "Frequency",
            "tickformat": ".,"
        },
        "yaxis": {
            "title": "Intensity",
            "tickformat": ".,"
        },
        "hovermode": "closest",
        "legend": {
            "x": 1.,
            "y": 1.
        }
    }
    return layout


def plot_spectrum(x, y, name):
    trace = go.Scatter(
        x=x,
        y=y,
        name=name
    )
    return trace
