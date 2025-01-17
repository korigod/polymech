import os
import math
import json
import csv

from polymech import compression, plot
from polymech.sources import kechekyan, yaml_metadata

DATA_DIR = 'data/2019.01.23'
PLOTS_DIR = 'plots/2019.01.23'

os.makedirs(PLOTS_DIR, exist_ok=True)

with open(os.path.join(DATA_DIR, 'samples.yaml')) as f:
    samples = yaml_metadata(f)

all_results = []
for sample in samples:
    # if sample['name'] != '65_CV':
    #     continue
    cross_section_sq_mm = math.pi * sample['diameter'] ** 2 / 4
    with open(os.path.join(DATA_DIR, sample['file']), 'rb') as f:
        results = compression.analyze(
            kechekyan(f), sample['length'], cross_section_sq_mm, sample['compression_rate']
        )
    sample['young_modulus'] = results.young_modulus.modulus / 1e9
    if results.yield_point is None:
        continue
    sample['yield_elongation'] = results.yield_point.elongation
    sample['yield_strength'] = results.yield_point.tension / 1e6
    sample['arzhakov'] = results.yield_point.elongation / (results.yield_point.tension / results.young_modulus.modulus)
    with open(os.path.join(PLOTS_DIR, f"{sample['name']}.png"), 'wb') as f:
        plot.stress_strain(results).savefig(f)
    all_results.append(results)
with open(os.path.join(PLOTS_DIR, 'all.png'), 'wb') as f:
    plot.stress_strain(all_results).savefig(f)
with open(os.path.join(PLOTS_DIR, 'comp_to_modulus.png'), 'wb') as f:
    comp_to_modulus = {
        s['plasticizer']: s['young_modulus'] for s in samples if 'А-ППО-А 540' in s['description']
    }
    plot.composition_to_modulus(comp_to_modulus).savefig(f)
with open(os.path.join(DATA_DIR, 'results.json'), 'w') as f:
    f.write(json.dumps(samples, indent=4, ensure_ascii=False))
with open(os.path.join(DATA_DIR, 'results.csv'), 'w') as f:
    w = csv.DictWriter(f, sample.keys())
    w.writeheader()
    w.writerows(samples)
