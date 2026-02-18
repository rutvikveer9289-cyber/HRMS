import pandas as pd
import os

file_path = r"d:\HRMS\rbis-hrms-main\files\Employee_Details.xlsx"
if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    print("Columns:", df.columns.tolist())
    print("First 5 rows:")
    print(df.head())
else:
    print("File not found.")
