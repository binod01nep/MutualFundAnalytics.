import sqlite3
import pandas as pd

conn = sqlite3.connect('bluestock_mf.db')
tables = pd.read_sql_query("SELECT name as Table_Name FROM sqlite_master WHERE type='table';", conn)

# Get row counts for each table
tables['Rows'] = tables['Table_Name'].apply(lambda t: pd.read_sql_query(f"SELECT COUNT(*) FROM {t}", conn).iloc[0,0])

print("\n=== Database Tables ===")
print(tables.to_string(index=False))
print("=======================\n")
conn.close()
