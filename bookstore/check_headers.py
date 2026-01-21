import openpyxl
import os

files = [
    r"D:\DA_SE347\Attributes.xlsx",
    r"D:\DA_SE347\Categories.xlsx",
    r"D:\DA_SE347\Products.xlsx"
]

for file_path in files:
    if os.path.exists(file_path):
        try:
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            headers = [cell.value for cell in sheet[1]]
            print(f"File: {os.path.basename(file_path)}")
            print(f"Headers: {headers}")
            print("-" * 20)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    else:
        print(f"File not found: {file_path}")
