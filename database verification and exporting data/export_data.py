# export_data.py
import sqlite3
import pandas as pd

conn = sqlite3.connect('world_data.db')

# Read and export
pd.read_sql("SELECT * FROM analysis_clean", conn).to_csv('world_data.csv', index=False)
pd.read_sql("SELECT * FROM country", conn).to_csv('country.csv', index=False)

conn.close()
