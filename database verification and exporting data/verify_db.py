# verify_db.py
import sqlite3
import pandas as pd

conn = sqlite3.connect('world_data.db')

# Check country data
countries = pd.read_sql("SELECT * FROM country LIMIT 5", conn)
print("Country data sample:")
print(countries)

# Check indicators
indicators = pd.read_sql("""
    SELECT * 
    FROM indicators 
    WHERE indicator_code IN ('NY.GDP.MKTP.CD', 'SP.POP.TOTL')
    LIMIT 10
""", conn)
print("\nIndicator data sample:")
print(indicators)

# Check data completeness
coverage = pd.read_sql("""
    SELECT 
        i.indicator_code,
        COUNT(DISTINCT i.country_code) AS countries_covered,
        MIN(i.year) AS first_year,
        MAX(i.year) AS last_year
    FROM indicators i
    GROUP BY i.indicator_code
""", conn)
print("\nData coverage:")
print(coverage)

conn.close()
