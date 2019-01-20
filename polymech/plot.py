from typing import BinaryIO
import matplotlib.backends.backend_agg as backend
from matplotlib.figure import Figure

from polymech.compression import CompressionResults


def stress_strain(results: CompressionResults) -> Figure:
    """
    To save the plot use Figure.savefig(file) method,
    where file is a path string or a BinaryIO
    """
    fig = Figure()
    backend.FigureCanvasAgg(fig)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(*results.processed_dataset.T)
    ax.plot(*zip(results.young_modulus.first_point, results.young_modulus.second_point), 'r-')
    ax.plot(results.yield_point.elongation, results.yield_point.tension, 'ro')
    return fig
