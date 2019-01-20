import math
import json
import csv

from polymech import compression
from polymech.sources import kechekyan, yaml_metadata
from polymech.plot import stress_strain

with open('data/samples.yaml') as f:
    samples = yaml_metadata(f)

for sample in samples:
    cross_section_sq_mm = math.pi * sample['diameter'] ** 2 / 4
    with open(f"data/{sample['file']}", 'rb') as f:
        results = compression.analyze(
            kechekyan(f), sample['length'], cross_section_sq_mm, sample['compression_rate']
        )
    sample['young_modulus'] = results.young_modulus.modulus / 1e9
    if results.yield_point is None:
        continue
    sample['yield_elongation'] = results.yield_point.elongation
    sample['yield_strength'] = results.yield_point.tension / 1e6
    sample['arzhakov'] = results.yield_point.elongation / (results.yield_point.tension / results.young_modulus.modulus)
    with open(f"plots/{sample['name']}.png", 'wb') as f:
        stress_strain(results).savefig(f)
with open('results.json', 'w') as f:
    f.write(json.dumps(samples, indent=4, ensure_ascii=False))
with open('results.csv', 'w') as f:
    w = csv.DictWriter(f, sample.keys())
    w.writeheader()
    w.writerows(samples)
