import os
import sys


DATA_DIR = 'data/2019.01.23'
YAML_FILENAME = 'samples.yaml'

YAML_TEMPLATE = '{test_parameters}\n\n---\n{samples}'

TESTS_PARAMETERS = (
    '# Compression rate in mm per second\n'
    'compression_rate: 5.0'
)

SAMPLE_TEMPLATE = """
- name: {name}
  description: 
  plasticizer: 0
  file: {filename}
  length: 
  diameter: 
"""

filenames = sorted([file for file in os.listdir(DATA_DIR) if file.endswith('.xlsx')])
samples = [SAMPLE_TEMPLATE.format(name=file[:-5], filename=file) for file in filenames]
yaml = YAML_TEMPLATE.format(test_parameters=TESTS_PARAMETERS, samples=''.join(samples))

with open(os.path.join(DATA_DIR, YAML_FILENAME), 'x') as f:
    f.write(yaml)
