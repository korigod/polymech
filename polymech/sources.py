from typing import BinaryIO, TextIO
import numpy as np
import xlrd
from ruamel import yaml


def kechekyan(xlsx_fd: BinaryIO) -> np.ndarray:
    book: xlrd.Book = xlrd.open_workbook(file_contents=xlsx_fd.read())
    sheet: xlrd.sheet.Sheet = book.sheet_by_index(0)
    timestamps = sheet.col_values(6, 1)
    forces = sheet.col_values(7, 1)
    return np.column_stack((timestamps, forces))


def yaml_metadata(yaml_fd: TextIO):
    yaml_obj = yaml.YAML(typ='safe')
    parsed = list(yaml_obj.load_all(yaml_fd))
    if len(parsed) == 1:
        return parsed[0]
    elif len(parsed) == 2:
        common_properties = parsed[0]
        samples = parsed[1]
        for sample in samples:
            for property_name, property_value in common_properties.items():
                if property_name not in sample:
                    sample[property_name] = property_value
        return samples
    else:
        raise Exception(f'Expected one or two documents in yaml file, got {len(parsed)}')
