from plotly.graph_objs import Figure

def plotly_to_html(fig:Figure, filename="out"):
    """
    Save a Plotly figure as an HTML file.

    Parameters
    ----------
    fig : plotly.graph_objs.Figure
        The Plotly figure to save.
    filename : str
        The name of the file to save the figure to.
    """
    fig.write_html(file = f"{filename}.html", full_html=True)