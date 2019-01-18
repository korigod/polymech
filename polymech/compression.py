from collections import namedtuple
from typing import Optional
import numpy as np

CompressionResults = namedtuple(
    'CompressionResults', (
        'young_modulus',
        'yield_point',
        'trimmed_dataset'
    )
)
YieldPoint = namedtuple('YieldPoint', ('index', 'timestamp', 'force'))
YoungModulus = namedtuple('YoungModulus', ('modulus', 'first_point', 'second_point'))


def _differentiate(dataset: np.ndarray) -> np.ndarray:
    dataset_x, dataset_y = dataset.T
    derivative = np.diff(dataset_y) / np.diff(dataset_x)
    return derivative


def _trim_dataset(dataset: np.ndarray) -> np.ndarray:
    max_force: float = max(dataset.T[1])
    start_force: float = dataset[0][1]
    max_force_for_init_period: float = start_force + 0.01 * (max_force - start_force)
    max_index_for_init_period: int = next(
        i for i, value in enumerate(dataset) if value[1] > max_force_for_init_period
    )
    init_period = dataset[:max_index_for_init_period]
    init_period_values_derivative = _differentiate(init_period)
    last_value_with_negative_derivative = [
        i for i, value in enumerate(init_period_values_derivative) if value < 0
    ][-1] + 1

    end_force: float = dataset[-1][1]
    number_of_equal_values_at_end = next(
        i for i, value in enumerate(reversed(dataset)) if value[1] != end_force
    )

    return dataset[last_value_with_negative_derivative:-number_of_equal_values_at_end]


def _find_yield_point(dataset: np.ndarray) -> Optional[YieldPoint]:
    derivative = _differentiate(dataset)
    yield_point = None
    for i, point in enumerate(derivative):
        if point < 0 and derivative[i - 1] > 0:
            previous_ten_points = derivative[i - 10:i]
            next_ten_points = derivative[i:i + 10]
            if any(p > 0 for p in previous_ten_points) and any(p < 0 for p in next_ten_points):
                yield_point = YieldPoint(i, *dataset[i])
                break
    return yield_point if yield_point is not None else None


def _calc_young_modulus(dataset: np.ndarray) -> YoungModulus:
    """
    Dataset must be trimmed and must end on the yield point or earlier.
    """
    max_derivative_index = np.argmax([
        dataset[i + 10][1] - dataset[i][1] for i in range(len(dataset) - 10)
    ])
    first_point = dataset[max_derivative_index]
    second_point = dataset[max_derivative_index + 10]
    modulus = (second_point[1] - first_point[1]) / (second_point[0] - first_point[0])
    return YoungModulus(modulus, first_point, second_point)


def analyze(dataset: np.ndarray) -> CompressionResults:
    # FIXME: sample geometry is not taken into account,
    # so Young's modulus is not calculated correctly.

    trimmed_dataset = _trim_dataset(dataset)
    yield_point = _find_yield_point(trimmed_dataset)
    if yield_point is None:
        raise Exception('Yield point detection failed')
    young_modulus = _calc_young_modulus(dataset[:yield_point.index])

    return CompressionResults(young_modulus, yield_point, trimmed_dataset)
