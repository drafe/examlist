from pathlib import Path
from openpyxl import load_workbook
# from openpyxl.utils import column_index_from_string as indx


def is_xlsx(f):
    xlsx = set(['.xlsx', '.xls'])
    return Path(f.name).suffix in xlsx


def handle_uploaded_file(f):
    wb = load_workbook(filename=f, read_only=True, data_only=True)
    return wb.sheetnames
