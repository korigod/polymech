import math
import json
import numpy as np

from polymech import compression
from polymech.sources import kechekyan


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, (
            np.int_, np.intc, np.intp, np.int8, np.int16, np.int32,
            np.int64, np.uint8, np.uint16, np.uint32, np.uint64
        )):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


source_filename = 'tests/data/01.xlsx'
with open(source_filename, 'rb') as f:
    dataset = kechekyan(f)
sample_length_mm = 13.47
sample_diameter_mm = 8.4
sample_cross_section_sq_mm = math.pi * sample_diameter_mm ** 2 / 4
compression_rate_mm_per_min = 5.0
trimmed_dataset = compression._trim_dataset(dataset.copy())
compression_part_of_dataset = compression._cutoff_decompression(trimmed_dataset.copy())
dataset_x_replaced = compression._timestamps_to_elongation(
    compression_part_of_dataset.copy(), sample_length_mm, compression_rate_mm_per_min
)
dataset_xy_replaced = compression._force_to_tension(
    dataset_x_replaced.copy(), sample_cross_section_sq_mm
)
yield_point = compression._find_yield_point(dataset_xy_replaced.copy())
if yield_point is None:
    raise Exception('Yield point detection failed')
young_modulus = compression._calc_young_modulus(dataset_xy_replaced.copy()[:yield_point.index])

test_data = {
    'source_filename': source_filename,
    'source_type': 'kechekyan',
    'sample_length_mm': sample_length_mm,
    'sample_cross_section_sq_mm': sample_cross_section_sq_mm,
    'compression_rate_mm_per_min': compression_rate_mm_per_min,
    'yield_point': yield_point._asdict(),
    'young_modulus': young_modulus._asdict(),
    'loaded_dataset': dataset,
    'trimmed_dataset': trimmed_dataset,
    'compression_part_of_dataset': compression_part_of_dataset,
    'dataset_x_replaced': dataset_x_replaced,
    'dataset_xy_replaced': dataset_xy_replaced
}

test_dump = json.dumps(test_data, indent=2, cls=NumpyEncoder)

with open('tests/data/01.json', 'w') as f:
    f.write(test_dump)
