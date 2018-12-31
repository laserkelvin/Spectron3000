
from plotly import graph_objs as go


def init_layout():
    layout = {
        "xaxis": {
            "title": "Frequency (MHz)",
            "tickformat": ".,"
        },
        "yaxis": {
            "title": "Flux (Jy/beam)",
            "tickformat": ".,"
        },
        "hovermode": "closest",
        "legend": {
            "x": 1.,
            "y": 1.
        }
    }
    return layout


def plot_spectrum(x, y, name, **kwargs):
    trace = go.Scattergl(
        x=x,
        y=y,
        name=name,
        **kwargs
    )
    return trace
