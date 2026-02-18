import pandas as pd
file_path = r"d:\HRMS\rbis-hrms-main\files\Employee_Details.xlsx"
df = pd.read_excel(file_path)
print(df['EmpId'].unique().tolist())
