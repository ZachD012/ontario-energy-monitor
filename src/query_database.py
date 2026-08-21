import sqlite3
import pandas as pd
from pathlib import Path
import plotly.express as px


DATABASE_FILE = Path("data/processed/energy.db")


connection = sqlite3.connect(DATABASE_FILE)

cursor = connection.cursor()


query = """
SELECT
    DATE(timestamp) AS date,

    SUM(CASE
        WHEN generation_type = 'Nuclear'
        THEN output_mwh
        ELSE 0
    END) AS nuclear_generation,

    SUM(CASE
        WHEN generation_type = 'Renewable'
        THEN output_mwh
        ELSE 0
    END) AS renewable_generation

FROM generation

GROUP BY DATE(timestamp)

ORDER BY date;
"""

cursor.execute(query)

rows = cursor.fetchall()

df = pd.DataFrame(
    rows,
    columns=["date", "nuclear_generation", "renewable_generation"]
)

df["date"] = pd.to_datetime(df["date"])

print("\nData types:")
print(df.dtypes)

print("\nFirst 10 rows from SQL:")
print(df.head(10))

import plotly.express as px

fig = px.line(
    df,
    x="date",
    y=["nuclear_generation", "renewable_generation"],
    title="Ontario Electricity Generation: Nuclear vs Renewable",
    labels={
        "date": "Date",
        "value": "Generation (MWh)",
        "variable": "Generation Type"
    }
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Generation (MWh)",
    legend_title="Generation Type",
    hovermode="x unified"
)

fig.show()

comparison_query = """
SELECT
    generation_type,
    ROUND(AVG(output_mwh), 2) AS average_generation,
    MIN(output_mwh) AS minimum_generation,
    MAX(output_mwh) AS maximum_generation
FROM generation
WHERE generation_type IN ('Nuclear', 'Renewable')
GROUP BY generation_type;
"""

cursor.execute(comparison_query)

comparison_rows = cursor.fetchall()

print("\nGeneration variability:")
for row in comparison_rows:
    print(row)

relative_output_query = """
WITH hourly_generation AS (

    SELECT
        timestamp,
        generation_type,
        SUM(output_mwh) AS hourly_output

    FROM generation

    WHERE generation_type IN ('Nuclear', 'Renewable')

    GROUP BY timestamp, generation_type
),

maximums AS (

    SELECT
        generation_type,
        MAX(hourly_output) AS maximum_output

    FROM hourly_generation

    GROUP BY generation_type
)

SELECT
    hourly_generation.timestamp,
    hourly_generation.generation_type,
    hourly_generation.hourly_output,
    maximums.maximum_output,

    ROUND(
        hourly_generation.hourly_output * 100.0
        / maximums.maximum_output,
        2
    ) AS percent_of_maximum

FROM hourly_generation

JOIN maximums
    ON hourly_generation.generation_type = maximums.generation_type

ORDER BY hourly_generation.timestamp;
"""

cursor.execute(relative_output_query)

relative_output_rows = cursor.fetchall()

relative_df = pd.DataFrame(
    relative_output_rows,
    columns=[
        "timestamp",
        "generation_type",
        "total_output",
        "maximum_output",
        "percent_of_maximum"
    ]
)

relative_df["timestamp"] = pd.to_datetime(
    relative_df["timestamp"]
)

print("\nRelative output DataFrame:")
print(relative_df.head(10))

fig2 = px.line(
    relative_df,
    x="timestamp",
    y="percent_of_maximum",
    color="generation_type",
    title="Generation as Percentage of Observed Maximum",
    labels={
        "timestamp": "Time",
        "percent_of_maximum": "Output (% of Observed Maximum)",
        "generation_type": "Generation Type"
    }
)

fig2.update_layout(
    hovermode="x unified"
)

fig2.show()

connection.close()