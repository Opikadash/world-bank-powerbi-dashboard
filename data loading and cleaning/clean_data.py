# clean_data.py
import sqlite3
import pandas as pd
import numpy as np

# Connect to database
conn = sqlite3.connect('world_data.db')

# Step 1: Clean country data
print("Cleaning country data...")
country_df = pd.read_sql("SELECT * FROM country", conn)

# Filter out aggregate regions (keep only real countries)
country_df = country_df[country_df['region'].notna()]

# Clean country names
country_df['country_name'] = country_df['country_name'].str.replace('&', 'and')
country_df['country_name'] = country_df['country_name'].str.replace(',', '')
country_df['country_name'] = country_df['country_name'].str.replace(r'\(.*\)', '', regex=True)
country_df['country_name'] = country_df['country_name'].str.strip()

# Step 2: Clean indicator data
print("Cleaning indicator data...")
indicators_df = pd.read_sql("SELECT * FROM indicators", conn)

# Filter to real countries only
indicators_df = indicators_df[indicators_df['country_code'].isin(country_df['country_code'])]

# Convert value to numeric and handle missing values
indicators_df['value'] = pd.to_numeric(indicators_df['value'], errors='coerce')

# Step 3: Create analysis view
print("Creating analysis view...")
analysis_df = pd.merge(
    indicators_df, 
    country_df[['country_code', 'country_name', 'region', 'income_group']],
    on='country_code',
    how='inner'
)

# Add decade column for aggregation
analysis_df['decade'] = (analysis_df['year'] // 10) * 10

# Calculate GDP per capita
print("Calculating GDP per capita...")
gdp_df = analysis_df[analysis_df['indicator_code'] == 'NY.GDP.MKTP.CD'][['country_code', 'year', 'value']]
pop_df = analysis_df[analysis_df['indicator_code'] == 'SP.POP.TOTL'][['country_code', 'year', 'value']]

merged_df = pd.merge(
    gdp_df.rename(columns={'value': 'gdp'}),
    pop_df.rename(columns={'value': 'population'}),
    on=['country_code', 'year'],
    how='inner'
)

merged_df['gdp_per_capita'] = merged_df['gdp'] / merged_df['population']

# Add back to main analysis
analysis_df = pd.merge(
    analysis_df,
    merged_df[['country_code', 'year', 'gdp_per_capita']],
    on=['country_code', 'year'],
    how='left'
)

# Step 4: Save cleaned data to new table
print("Saving cleaned data...")
analysis_df.to_sql('analysis_clean', conn, if_exists='replace', index=False)

# Create indexes
with conn:
    conn.execute("CREATE INDEX idx_clean_country ON analysis_clean(country_code)")
    conn.execute("CREATE INDEX idx_clean_year ON analysis_clean(year)")
    conn.execute("CREATE INDEX idx_clean_indicator ON analysis_clean(indicator_code)")

# Verify cleaned data
print("Verifying cleaned data...")
clean_sample = pd.read_sql("SELECT * FROM analysis_clean LIMIT 5", conn)
clean_count = pd.read_sql("SELECT COUNT(*) FROM analysis_clean", conn)
regions = pd.read_sql("SELECT DISTINCT region FROM analysis_clean", conn)

print("\nCleaned data sample:")
print(clean_sample)
print(f"\nTotal records: {clean_count.iloc[0,0]}")
print("\nRegions:")
print(regions)

conn.close()
