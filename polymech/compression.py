from collections import namedtuple
from typing import Optional
import numpy as np

CompressionResults = namedtuple(
    'CompressionResults', (
        'young_modulus',
        'yield_point',
        'processed_dataset'
    )
)
YieldPoint = namedtuple('YieldPoint', ('index', 'elongation', 'tension'))
YoungModulus = namedtuple('YoungModulus', ('modulus', 'first_point', 'second_point'))


def _differentiate(dataset: np.ndarray) -> np.ndarray:
    dataset_x, dataset_y = dataset.T
    derivative = np.diff(dataset_y) / np.diff(dataset_x)
    return derivative


def _timestamps_to_elongation(dataset: np.ndarray, sample_length_mm: float,
                              compression_rate_mm_per_min: float) -> np.ndarray:
    dataset_T = dataset.T
    zero_elongation_timestamp = dataset_T[0][0]
    compression_rate_mm_per_sec = compression_rate_mm_per_min / 60
    dataset_T[0] -= zero_elongation_timestamp
    dataset_T[0] = (dataset_T[0] * compression_rate_mm_per_sec) / sample_length_mm
    return dataset_T.T


def _force_to_tension(dataset: np.ndarray, sample_cross_section_sq_mm: float) -> np.ndarray:
    dataset_T = dataset.T
    sample_cross_section_sq_m = sample_cross_section_sq_mm / 1000000
    dataset_T[1] = dataset_T[1] / sample_cross_section_sq_m
    return dataset_T.T


def _trim_dataset(dataset: np.ndarray) -> np.ndarray:
    max_force: float = max(dataset.T[1])
    start_force: float = dataset[0][1]
    max_force_for_init_period: float = start_force + 0.01 * (max_force - start_force)
    max_index_for_init_period: int = next(
        i for i, value in enumerate(dataset) if value[1] > max_force_for_init_period
    )
    init_period = dataset[:max_index_for_init_period]
    init_period_values_derivative = _differentiate(init_period)
    values_with_negative_derivative = [
        i for i, value in enumerate(init_period_values_derivative) if value < 0
    ]
    if values_with_negative_derivative:
        last_value_with_negative_derivative = values_with_negative_derivative[-1] + 1
    else:
        last_value_with_negative_derivative = 0

    end_force: float = dataset[-1][1]
    number_of_equal_values_at_end = next(
        i for i, value in enumerate(reversed(dataset)) if value[1] != end_force
    )

    return dataset[last_value_with_negative_derivative:-number_of_equal_values_at_end]


def _cutoff_decompression(dataset: np.ndarray) -> np.ndarray:
    derivative = _differentiate(dataset)
    values_to_cut_count = next(
        i for i, value in enumerate(reversed(derivative)) if value > 0
    )
    return dataset[:-values_to_cut_count]


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
    segment_x_length: int = len(dataset) // 10
    max_derivative_index = np.argmax([
        dataset[i + segment_x_length][1] - dataset[i][1]
        for i in range(len(dataset) - segment_x_length)
    ])
    first_point = dataset[max_derivative_index]
    second_point = dataset[max_derivative_index + segment_x_length]
    modulus = (second_point[1] - first_point[1]) / (second_point[0] - first_point[0])
    return YoungModulus(modulus, first_point, second_point)


def analyze(dataset: np.ndarray, sample_length_mm: float, sample_cross_section_sq_mm: float,
            compression_rate_mm_per_min: float) -> CompressionResults:
    trimmed_dataset = _trim_dataset(dataset)
    compression_part_of_dataset = _cutoff_decompression(trimmed_dataset)
    dataset_x_replaced = _timestamps_to_elongation(
        compression_part_of_dataset, sample_length_mm, compression_rate_mm_per_min
    )
    dataset_xy_replaced = _force_to_tension(
        dataset_x_replaced, sample_cross_section_sq_mm
    )
    yield_point = _find_yield_point(dataset_xy_replaced)
    if yield_point is None:
        raise Exception('Yield point detection failed')
    young_modulus = _calc_young_modulus(dataset_xy_replaced[:yield_point.index])

    return CompressionResults(young_modulus, yield_point, dataset_xy_replaced)
