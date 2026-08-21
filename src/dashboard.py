import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATABASE_FILE = Path("data/processed/energy.db")


st.set_page_config(
    page_title="Ontario Energy Monitor",
    page_icon="⚡",
    layout="wide"
)

st.title("Ontario Energy Monitor")

st.write(
    "An interactive exploration of Ontario electricity generation "
    "using publicly available IESO data."
)


st.sidebar.header("Filters")

start_date = st.sidebar.date_input(
    "Start date",
    value=pd.Timestamp("2026-01-01").date()
)

end_date = st.sidebar.date_input(
    "End date",
    value=pd.Timestamp("2026-08-19").date()
)

start_date = start_date.strftime("%Y-%m-%d")
end_date = end_date.strftime("%Y-%m-%d")

if start_date > end_date:
    st.error("Start date must be before or equal to the end date.")
    st.stop()

st.sidebar.write(
    f"Selected period: {start_date} to {end_date}"
)

def get_latest_timestamp():
    connection = sqlite3.connect(DATABASE_FILE)

    query = """
    SELECT MAX(timestamp)
    FROM generation;
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return result.iloc[0, 0]

latest_timestamp = pd.to_datetime(
    get_latest_timestamp()
)

formatted_timestamp = latest_timestamp.strftime(
    "%B %d, %Y at %H:%M"
)

st.sidebar.caption(
    f"Data through: {formatted_timestamp}"
)


def get_relative_output(start_date, end_date):
    connection = sqlite3.connect(DATABASE_FILE)

    query = """
    WITH hourly_generation AS (
        SELECT
            timestamp,
            generation_type,
            SUM(output_mwh) AS total_output

        FROM generation

        WHERE generation_type IN ('Nuclear', 'Renewable')
        AND DATE(timestamp) BETWEEN ? AND ?

        GROUP BY
            timestamp,
            generation_type
    ),

    maximums AS (
        SELECT
            generation_type,
            MAX(total_output) AS maximum_output

        FROM hourly_generation

        GROUP BY generation_type
    )

    SELECT
        hourly_generation.timestamp,
        hourly_generation.generation_type,
        hourly_generation.total_output,
        maximums.maximum_output,

        ROUND(
            hourly_generation.total_output * 100.0
            / maximums.maximum_output,
            2
        ) AS percent_of_maximum

    FROM hourly_generation

    JOIN maximums
        ON hourly_generation.generation_type = maximums.generation_type

    ORDER BY hourly_generation.timestamp;
    """

    df = pd.read_sql_query(
        query,
        connection,
        params=(start_date, end_date)
    )

    connection.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def get_dashboard_metrics(start_date, end_date):
    connection = sqlite3.connect(DATABASE_FILE)

    query = """
    SELECT
        SUM(output_mwh) AS total_generation,

        SUM(
            CASE
                WHEN generation_type IN ('Nuclear', 'Renewable')
                THEN output_mwh
                ELSE 0
            END
        ) AS low_carbon_generation,

        SUM(
            CASE
                WHEN generation_type = 'Nuclear'
                THEN output_mwh
                ELSE 0
            END
        ) AS nuclear_generation,

        SUM(
            CASE
                WHEN generation_type = 'Renewable'
                THEN output_mwh
                ELSE 0
            END
        ) AS renewable_generation

    FROM generation

    WHERE DATE(timestamp) BETWEEN ? AND ?;
    """

    df = pd.read_sql_query(
        query,
        connection,
        params=(start_date, end_date)
    )

    connection.close()

    return df


def calculate_metrics(df):
    total = df.loc[0, "total_generation"]

    low_carbon = (
        df.loc[0, "low_carbon_generation"]
        / total
        * 100
    )

    nuclear = (
        df.loc[0, "nuclear_generation"]
        / total
        * 100
    )

    renewable = (
        df.loc[0, "renewable_generation"]
        / total
        * 100
    )

    return {
        "low_carbon": round(low_carbon, 2),
        "nuclear": round(nuclear, 2),
        "renewable": round(renewable, 2)
    }



def create_relative_output_chart(df):
    fig = px.line(
        df,
        x="timestamp",
        y="percent_of_maximum",
        color="generation_type",
        title="Generation Relative to Observed Maximum",
        labels={
            "timestamp": "Time",
            "percent_of_maximum": "Percent of Observed Maximum (%)",
            "generation_type": "Generation Type"
        }
    )

    fig.update_layout(
        hovermode="x unified"
    )

    return fig


def get_daily_generation(start_date, end_date):
    connection = sqlite3.connect(DATABASE_FILE)

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

    WHERE DATE(timestamp) BETWEEN ? AND ?

    GROUP BY DATE(timestamp)

    ORDER BY date;
    """

    df = pd.read_sql_query(
    query,
    connection,
    params=(start_date, end_date)
    )

    connection.close()

    df["date"] = pd.to_datetime(df["date"])

    return df


def create_generation_chart(df):
    fig = px.line(
        df,
        x="date",
        y=["nuclear_generation", "renewable_generation"],
        title="Ontario Nuclear vs Renewable Generation",
        labels={
            "date": "Date",
            "value": "Generation (MWh)",
            "variable": "Generation Type"
        }
    )

    fig.update_layout(
        hovermode="x unified"
    )

    return fig


def get_generation_mix(start_date, end_date):
    connection = sqlite3.connect(DATABASE_FILE)

    query = """
    SELECT
        fuel_type,
        SUM(output_mwh) AS total_generation,

        ROUND(
            SUM(output_mwh) * 100.0 /
            (
                SELECT SUM(output_mwh)
                FROM generation
                WHERE DATE(timestamp) BETWEEN ? AND ?
            ),
            2
        ) AS percentage_of_total

    FROM generation

    WHERE DATE(timestamp) BETWEEN ? AND ?

    GROUP BY fuel_type

    ORDER BY total_generation DESC;
    """

    df = pd.read_sql_query(
        query,
        connection,
        params=(
            start_date,
            end_date,
            start_date,
            end_date
        )
    )

    connection.close()

    return df


def create_generation_mix_chart(df):

    fig = px.bar(
        df,
        x="fuel_type",
        y="percentage_of_total",
        title="Ontario Generation Mix",
        labels={
            "fuel_type": "Fuel Type",
            "percentage_of_total": "Share of Generation (%)"
        },
        text="percentage_of_total"
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    return fig


metrics_df = get_dashboard_metrics(
    start_date,
    end_date
)

metrics = calculate_metrics(metrics_df)

st.subheader("Generation Mix")

col1, col2, col3 = st.columns(3)


with col1:
    st.metric(
        "Low-Carbon Generation",
        f"{metrics['low_carbon']}%"
    )

with col2:
    st.metric(
        "Nuclear Generation",
        f"{metrics['nuclear']}%"
    )

with col3:
    st.metric(
        "Renewable Generation",
        f"{metrics['renewable']}%"
    )

daily_df = get_daily_generation(
    start_date,
    end_date
)

daily_fig = create_generation_chart(daily_df)

st.plotly_chart(
    daily_fig,
    use_container_width=True
)


relative_df = get_relative_output(
    start_date,
    end_date
)

relative_fig = create_relative_output_chart(relative_df)

st.plotly_chart(
    relative_fig,
    use_container_width=True
)

st.caption(
    "Relative output represents generation as a percentage of the "
    "maximum observed output for each generation type within the "
    "selected date range. It should not be interpreted as installed "
    "generating capacity or a direct measure of reliability."
)


mix_df = get_generation_mix(
    start_date,
    end_date
)

mix_fig = create_generation_mix_chart(
    mix_df
)

st.plotly_chart(
    mix_fig,
    use_container_width=True
)


st.divider()

st.subheader("Data Source")

st.write(
    "Generation data is sourced from publicly available electricity "
    "generation data provided by the Independent Electricity System "
    "Operator (IESO)."
)

st.caption(
    "This dashboard is an independent portfolio project and is not "
    "affiliated with or endorsed by the IESO."
)
