import sqlite3
from pathlib import Path


DATABASE_FILE = Path("data/processed/energy.db")


connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()

query = """
SELECT
    fuel_type,
    SUM(output_mwh) AS total_generation
FROM generation
GROUP BY fuel_type
ORDER BY total_generation DESC;
"""

cursor.execute(query)

rows = cursor.fetchall()

print("\nFirst 10 rows from SQL:")

for row in rows:
    print(row)

connection.close()