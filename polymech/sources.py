import numpy as np
import xlrd


def kechekyan(xlsx_path: str) -> np.ndarray:
    book: xlrd.Book = xlrd.open_workbook(xlsx_path)
    sheet: xlrd.sheet.Sheet = book.sheet_by_index(0)
    timestamps = sheet.col_values(6, 1)
    forces = sheet.col_values(7, 1)
    return np.column_stack((timestamps, forces))
