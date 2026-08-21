# Ontario Energy Monitor

A data analytics and visualization project using publicly available electricity generation data from the Independent Electricity System Operator (IESO).

Ontario Energy Monitor downloads, parses, validates, and analyzes hourly Ontario electricity generation data using **Python, SQL, and SQLite**, then presents the results through an interactive **Streamlit and Plotly dashboard**.

## Project Overview

The project analyzes Ontario's electricity generation mix with a focus on nuclear and renewable generation.

It demonstrates:

- Python data ingestion and XML parsing
- Data transformation and validation
- SQL analysis with SQLite
- Interactive data visualization
- Automated data updates

## Architecture

```text
IESO Public Data
       ↓
Python Data Ingestion
       ↓
XML Parsing & Transformation
       ↓
Data Validation
       ↓
SQLite Database
       ↓
SQL Analysis
       ↓
Streamlit Dashboard
```

### Technologies

Python · pandas · requests · XML · SQLite · SQL · Plotly · Streamlit · Git/GitHub · Windows Task Scheduler

## Data Pipeline

The pipeline is divided into several stages:

**Ingestion** — `fetch_ieso_generation.py` downloads the latest IESO XML data.

**Parsing** — `parse_ieso_generation.py` extracts date, hour, fuel type, generation output, and output quality from the XML.

**Transformation & Validation** — `load_database.py` classifies generation sources as Nuclear, Renewable, Fossil, or Other, creates timestamps, and validates the dataset.

**Database** — Transformed data is stored in a SQLite `generation` table.

**Updates** — `update_data.py` runs the complete pipeline to download, process, validate, and rebuild the database.

## SQL Analysis

SQL is used to analyze generation trends and create datasets for the dashboard.

Examples include:

- Total generation by fuel type
- Daily nuclear vs. renewable generation
- Low-carbon generation percentage
- Average, minimum, and maximum generation output
- Generation output relative to observed maximum

For this project, **low-carbon generation is defined as Nuclear + Renewable**.

## Dashboard

The Streamlit dashboard provides interactive views of Ontario electricity generation, including:

- Nuclear vs. renewable generation over time
- Generation output relative to observed maximum
- Generation mix by source
- Interactive date filtering
- Generation mix percentages

The dashboard uses Plotly for interactive visualizations.

## Automated Updates

Windows Task Scheduler runs the data update pipeline automatically:

```text
update_data.py
      ↓
Download latest IESO data
      ↓
Parse & transform
      ↓
Validate
      ↓
Rebuild SQLite database
```

This allows the dashboard's underlying data to be refreshed without manually downloading the source file.

## Project Structure

```text
ontario-energy-monitor/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── fetch_ieso_generation.py
│   ├── parse_ieso_generation.py
│   ├── load_database.py
│   ├── query_database.py
│   ├── analyze_generation.py
│   ├── dashboard.py
│   └── update_data.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Key Findings

The analyzed data shows distinct generation profiles across Ontario's electricity sources.

Nuclear generation demonstrates a relatively narrow observed output range, while renewable generation shows substantially greater variation.

These observations describe the generation patterns in the dataset and should not be interpreted as standalone measures of reliability.

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Update the data:

```bash
python src/update_data.py
```

Run SQL analysis:

```bash
python src/query_database.py
```

Launch the dashboard:

```bash
streamlit run src/dashboard.py
```

## Future Improvements

- Public dashboard deployment
- Additional IESO datasets
- Electricity demand analysis
- Additional energy-market metrics
- Improved monitoring of automated updates
- Cloud-based data pipeline