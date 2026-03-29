import pandas as pd
import sqlite3

df = pd.read_excel('calorie_data.xlsx')
print(df)

db = sqlite3.connect('menu.db')
dfs = pd.read_excel('calorie_data.xlsx', sheet_name='calorie_data')

for table, df in dfs.items():
    df.to_sql(table, db)
    print(f'{df} inserted successfully')