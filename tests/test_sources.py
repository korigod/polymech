import json
import pytest
import numpy as np

from polymech import sources


@pytest.fixture
def dataset_xlsx_fd(request):
    with open(request.param, 'rb') as fd:
        yield fd


@pytest.fixture(scope='module')
def dataset_d(request):
    with open(request.param) as fd:
        yield json.load(fd)


@pytest.mark.parametrize(
    'dataset_xlsx_fd, dataset_d', [
        ('tests/data/01.xlsx', 'tests/data/01.json')
    ], indirect=True
)
def test_kechekyan(dataset_xlsx_fd, dataset_d):
    dataset_loaded: np.ndarray = sources.kechekyan(dataset_xlsx_fd)
    assert isinstance(dataset_loaded, np.ndarray)
    assert np.array_equal(dataset_loaded, dataset_d['loaded_dataset'])
