import json
import pytest
import numpy as np

from polymech import compression


@pytest.fixture(scope='module', params=['tests/data/01.json'])
def dataset_d(request):
    with open(request.param) as fd:
        data = json.load(fd)
        numpy_data = {k: np.array(v) if isinstance(v, list) else v for k, v in data.items()}
        yield numpy_data


def test_trim(dataset_d):
    assert np.array_equal(
        dataset_d['trimmed_dataset'],
        compression._trim_dataset(dataset_d['loaded_dataset'])
    )


def test_cutoff_decompression(dataset_d):
    assert np.array_equal(
        dataset_d['compression_part_of_dataset'],
        compression._cutoff_decompression(dataset_d['trimmed_dataset'])
    )


def test_timestamps_to_elongation_conversion(dataset_d):
    assert np.array_equal(
        dataset_d['dataset_x_replaced'],
        compression._timestamps_to_elongation(
            dataset_d['compression_part_of_dataset'],
            dataset_d['sample_length_mm'],
            dataset_d['compression_rate_mm_per_min']
        )
    )


def test_force_to_tension_conversion(dataset_d):
    assert np.array_equal(
        dataset_d['dataset_xy_replaced'],
        compression._force_to_tension(
            dataset_d['dataset_x_replaced'],
            dataset_d['sample_cross_section_sq_mm']
        )
    )


def test_yield_point_detection(dataset_d):
    assert compression._find_yield_point(dataset_d['dataset_xy_replaced'])._asdict() == \
        dataset_d['yield_point']


def test_young_modulus_calculation(dataset_d):
    yield_point_index = dataset_d['yield_point']['index']
    input_dataset = dataset_d['dataset_xy_replaced'][:yield_point_index]
    young_modulus_d = compression._calc_young_modulus(input_dataset)._asdict()

    assert young_modulus_d['modulus'] == dataset_d['young_modulus']['modulus']
    assert np.array_equal(
        young_modulus_d['first_point'], dataset_d['young_modulus']['first_point']
    )
    assert np.array_equal(
        young_modulus_d['second_point'], dataset_d['young_modulus']['second_point']
    )
