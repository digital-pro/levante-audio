# import pandas lib as pd
import pandas as pd
import openpyxl

# read by default 1st sheet of an excel file
spanish_data_file = './data/Tasks_ItemBank_Spanish.xlsx'
spanish_dataframe = pd.read_excel(spanish_data_file)

print(spanish_dataframe)

# read by default 1st sheet of an excel file
german_data_file = './data/Tasks_ItemBank_German.xlsx'
german_dataframe = pd.read_excel(german_data_file)

print(german_dataframe)
