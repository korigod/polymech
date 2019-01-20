from typing import BinaryIO, Iterable, Union
import matplotlib.backends.backend_agg as backend
from matplotlib.figure import Figure

from polymech.compression import CompressionResults


def stress_strain(
    results: Union[CompressionResults, Iterable[CompressionResults]]
) -> Figure:
    """
    To save the plot use Figure.savefig(file) method,
    where file is a path string or a BinaryIO.
    """
    figure = Figure()
    backend.FigureCanvasAgg(figure)
    axes = figure.add_subplot(1, 1, 1)
    if isinstance(results, CompressionResults):
        results = [results]
    for result in results:
        axes.plot(*result.processed_dataset.T)
        axes.plot(*zip(result.young_modulus.first_point, result.young_modulus.second_point), 'r-')
        axes.plot(result.yield_point.elongation, result.yield_point.tension, 'ro')
    return figure
