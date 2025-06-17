import sqlite3
import pandas as pd
import os
import requests
from zipfile import ZipFile
from io import BytesIO

# Download and extract data if not exists
def download_data():
    url = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
    print("Downloading dataset...")
    response = requests.get(url)
    zipfile = ZipFile(BytesIO(response.content))
    zipfile.extractall()
    print("Files extracted:")
    print(zipfile.namelist())
    return zipfile.namelist()

# Check if files exist
extracted_files = []
if not any(f.endswith('.csv') for f in os.listdir()):
    extracted_files = download_data()

# Find the actual country and data files
country_file = 'WDICountry.csv'
data_file = 'WDICSV.csv'  # CORRECT DATA FILE

if not os.path.exists(country_file):
    raise FileNotFoundError(f"Country file not found: {country_file}")
if not os.path.exists(data_file):
    raise FileNotFoundError(f"Data file not found: {data_file}")

print(f"Using country file: {country_file}")
print(f"Using data file: {data_file}")

# Create database
conn = sqlite3.connect('world_data.db')

# Load data
try:
    print(f"Loading country data from {country_file}...")
    country_df = pd.read_csv(country_file)
    
    print(f"Loading indicator data from {data_file}...")
    indicators_df = pd.read_csv(data_file)
except Exception as e:
    print(f"Error loading data: {e}")
    conn.close()
    exit()

# Clean country data
print("Processing country data...")
country_df = country_df[['Country Code', 'Short Name', 'Region', 'Income Group']]
country_df.columns = ['country_code', 'country_name', 'region', 'income_group']
country_df = country_df.dropna(subset=['country_code'])

# Clean indicator data
print("Processing indicator data...")
# Reshape indicators (wide to long format)
indicators_long = pd.melt(
    indicators_df,
    id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'],
    var_name='year',
    value_name='value'
)
indicators_long.columns = ['country_name', 'country_code', 'indicator_name', 'indicator_code', 'year', 'value']

# Convert year to numeric and filter valid years
indicators_long['year'] = pd.to_numeric(indicators_long['year'], errors='coerce')
indicators_long = indicators_long.dropna(subset=['year'])
indicators_long['year'] = indicators_long['year'].astype(int)

# Filter to key indicators (GDP, Population)
key_indicators = ['NY.GDP.MKTP.CD', 'SP.POP.TOTL', 'NY.GDP.PCAP.CD']
indicators_long = indicators_long[indicators_long['indicator_code'].isin(key_indicators)]

# Save to SQLite
print("Saving to SQLite database...")
country_df.to_sql('country', conn, if_exists='replace', index=False)
indicators_long.to_sql('indicators', conn, if_exists='replace', index=False)

# Add indexes
print("Creating indexes...")
with conn:
    conn.execute("CREATE INDEX idx_country_code ON country(country_code)")
    conn.execute("CREATE INDEX idx_indicators_code ON indicators(indicator_code)")
    conn.execute("CREATE INDEX idx_indicators_country ON indicators(country_code)")
    conn.execute("CREATE INDEX idx_indicators_year ON indicators(year)")

print("Database created successfully!")
print(f"Database location: {os.path.abspath('world_data.db')}")
print(f"Country records: {len(country_df)}")
print(f"Indicator records: {len(indicators_long)}")

conn.close()
