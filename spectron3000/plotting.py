
from plotly import graph_objs as go


def init_layout():
    """
    Initializes a layout dict for Plotly figures.
    :return:
    """
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
    """
    Generates a Plotly scatter plot with the Scattergl function.
    This function specifically optimizes for performance, given that the
    datasets we're dealing with generally have many thousands of points.
    :param x: np.array of x values
    :param y: np.array of y values
    :param name: str denoting the legend value
    :param kwargs: additional kwargs for specifying the plot
    :return: Scattergl object
    """
    trace = go.Scattergl(
        x=x,
        y=y,
        name=name,
        **kwargs
    )
    return trace
