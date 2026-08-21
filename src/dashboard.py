import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATABASE_FILE = Path("data/processed/energy.db")


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Ontario Energy Monitor",
    page_icon="⚡",
    layout="wide"
)


# ============================================================
# COLOR PALETTE
# ============================================================

YELLOW = "#E8D823"
GOLD = "#B5AB3F"
OLIVE = "#827D48"
DARK_OLIVE = "#4F4D3B"
DARK = "#33322B"
LIGHT_TEXT = "#F4F1D0"


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    f"""
    <style>

    /* Main application */
    .stApp {{
        background-color: {DARK};
        color: {LIGHT_TEXT};
    }}

    /* Main content width */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    /* Headings */
    h1 {{
        color: {YELLOW} !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }}

    h2, h3 {{
        color: {LIGHT_TEXT} !important;
    }}

    /* Regular text */
    p {{
        color: {LIGHT_TEXT};
    }}

    /* Date filter container */
    .date-filter {{
        background-color: {DARK_OLIVE};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1.5rem 0 2rem 0;
        border-left: 5px solid {YELLOW};
    }}

    /* KPI cards */
    /* Major KPI cards */
    .major-kpi {{
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 18px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.15);
        background-color: {DARK_OLIVE};
    }}

    .major-kpi-mwh {{
        font-size: 17px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 6px;
    }}

    .major-kpi-title {{
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: {YELLOW};
    }}

    .major-kpi-value {{
        font-size: 42px;
        font-weight: 800;
        margin: 8px 0;
        color: {YELLOW};
    }}

    .major-kpi-description {{
        font-size: 14px;
        opacity: 0.8;
    }}

    /* Smaller KPI cards */
    .minor-kpi {{
        background-color: {DARK_OLIVE};
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .minor-kpi-mwh {{
        font-size: 13px;
        font-weight: 500;
        color: #FFFFFF;
        opacity: 0.75;
        margin-top: 4px;
    }}

    .minor-kpi-title {{
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
        color: {GOLD};
    }}

    .minor-kpi-value {{
        font-size: 27px;
        font-weight: 700;
        margin-top: 5px;
        color: {GOLD};
    }}

    /* Section spacing */
    .section-header {{
        margin-top: 2rem;
        margin-bottom: 1rem;
    }}

    /* Divider */
    hr {{
        border-color: {DARK_OLIVE} !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {DARK_OLIVE};
    }}

    [data-testid="stSidebar"] * {{
        color: {LIGHT_TEXT};
    }}

    /* Date inputs */
    [data-testid="stDateInput"] label {{
        color: {LIGHT_TEXT} !important;
    }}

    /* Streamlit metric fallback */
    [data-testid="stMetric"] {{
        background-color: {DARK_OLIVE};
        padding: 1rem;
        border-radius: 10px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.title("Ontario Energy Monitor")

st.write(
    "An interactive exploration of Ontario electricity generation "
    "using publicly available IESO data."
)


# ============================================================
# DATE FILTER
# ============================================================


st.subheader("Date Range")

filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])

with filter_col1:
    start_date = st.date_input(
        "Start date",
        value=pd.Timestamp("2026-01-01").date()
    )

with filter_col2:
    end_date = st.date_input(
        "End date",
        value=pd.Timestamp("2026-08-19").date()
    )

start_date = start_date.strftime("%Y-%m-%d")
end_date = end_date.strftime("%Y-%m-%d")

if start_date > end_date:
    st.error("Start date must be before or equal to the end date.")
    st.stop()

with filter_col3:
    st.write("")
    st.write("")
    st.caption(
        f"Selected period: **{start_date} → {end_date}**"
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

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
        ON hourly_generation.generation_type =
           maximums.generation_type

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
        ) AS renewable_generation,

        SUM(
            CASE
                WHEN generation_type = 'Fossil'
                THEN output_mwh
                ELSE 0
            END
        ) AS fossil_generation,

        SUM(
            CASE
                WHEN generation_type = 'Other'
                THEN output_mwh
                ELSE 0
            END
        ) AS other_generation

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


def format_mwh(value):
    return f"{value:,.0f} MWh"


def calculate_metrics(df):

    total = df.loc[0, "total_generation"]

    low_carbon_mwh = df.loc[0, "low_carbon_generation"]
    nuclear_mwh = df.loc[0, "nuclear_generation"]
    renewable_mwh = df.loc[0, "renewable_generation"]
    fossil_mwh = df.loc[0, "fossil_generation"]
    other_mwh = df.loc[0, "other_generation"]

    low_carbon = (
        low_carbon_mwh
        / total
        * 100
    )

    fossil_other = (
        (fossil_mwh + other_mwh)
        / total
        * 100
    )

    nuclear = (
        nuclear_mwh
        / total
        * 100
    )

    renewable = (
        renewable_mwh
        / total
        * 100
    )

    fossil = (
        fossil_mwh
        / total
        * 100
    )

    other = (
        other_mwh
        / total
        * 100
    )

    return {
        "low_carbon": round(low_carbon, 2),
        "low_carbon_mwh": low_carbon_mwh,

        "fossil_other": round(fossil_other, 2),
        "fossil_other_mwh": fossil_mwh + other_mwh,

        "nuclear": round(nuclear, 2),
        "nuclear_mwh": nuclear_mwh,

        "renewable": round(renewable, 2),
        "renewable_mwh": renewable_mwh,

        "fossil": round(fossil, 2),
        "fossil_mwh": fossil_mwh,

        "other": round(other, 2),
        "other_mwh": other_mwh
    }


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


# ============================================================
# PLOTLY CHARTS
# ============================================================

def apply_chart_theme(fig):

    fig.update_layout(
        paper_bgcolor=DARK,
        plot_bgcolor=DARK,
        font=dict(
            color=LIGHT_TEXT
        ),
        title_font=dict(
            color=YELLOW,
            size=20
        ),
        legend=dict(
            font=dict(
                color=LIGHT_TEXT
            )
        ),
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        )
    )

    fig.update_xaxes(
        gridcolor=DARK_OLIVE,
        zerolinecolor=DARK_OLIVE
    )

    fig.update_yaxes(
        gridcolor=DARK_OLIVE,
        zerolinecolor=DARK_OLIVE
    )

    return fig


def create_generation_chart(df):

    fig = px.line(
        df,
        x="date",
        y=[
            "nuclear_generation",
            "renewable_generation"
        ],
        title="Ontario Nuclear vs Renewable Generation",
        labels={
            "date": "Date",
            "value": "Generation (MWh)",
            "variable": "Generation Type"
        },
        color_discrete_sequence=[
            YELLOW,
            GOLD
        ]
    )

    fig.update_layout(
        hovermode="x unified"
    )

    return apply_chart_theme(fig)


def create_relative_output_chart(df):

    fig = px.line(
        df,
        x="timestamp",
        y="percent_of_maximum",
        color="generation_type",
        title="Generation Relative to Observed Maximum",
        labels={
            "timestamp": "Time",
            "percent_of_maximum":
                "Percent of Observed Maximum (%)",
            "generation_type": "Generation Type"
        },
        color_discrete_sequence=[
            YELLOW,
            GOLD
        ]
    )

    fig.update_layout(
        hovermode="x unified"
    )

    return apply_chart_theme(fig)


def create_generation_mix_chart(df):

    fig = px.bar(
        df,
        x="fuel_type",
        y="percentage_of_total",
        title="Ontario Generation Mix",
        labels={
            "fuel_type": "Fuel Type",
            "percentage_of_total":
                "Share of Generation (%)"
        },
        text="percentage_of_total",
        color="fuel_type",
        color_discrete_sequence=[
            YELLOW,
            GOLD,
            OLIVE,
            DARK_OLIVE,
            "#6B674D",
            "#96905A",
            "#C4BC69"
        ]
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    return apply_chart_theme(fig)


# ============================================================
# GENERATION KPI SECTION
# ============================================================

metrics_df = get_dashboard_metrics(
    start_date,
    end_date
)

metrics = calculate_metrics(metrics_df)

st.subheader("Generation Overview")

# Major generation categories

kpiMjr_col1, kpiMjr_col2,  = st.columns(2)


with kpiMjr_col1:

    st.markdown(
        f"""
        <div class="major-kpi low-carbon">
            <div class="major-kpi-title">LOW-CARBON</div>
            <div class="major-kpi-value">
                {metrics['low_carbon']}%
            </div>
            <div class="major-kpi-mwh">
                {format_mwh(metrics['low_carbon_mwh'])}
            </div>
            <div class="major-kpi-description">
                Nuclear + Renewable
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with kpiMjr_col2:

    st.markdown(
        f"""
        <div class="major-kpi fossil-other">
            <div class="major-kpi-title">FOSSIL / OTHER</div>
            <div class="major-kpi-value">
                {metrics['fossil_other']}%
            </div>
            <div class="major-kpi-mwh">
                {format_mwh(metrics['fossil_other_mwh'])}
            </div>
            <div class="major-kpi-description">
                Gas + Other
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Individual generation sources
kpiMin_col1, kpiMin_col2, kpiMin_col3, kpiMin_col4 = st.columns(4)

with kpiMin_col1:

    st.markdown(
        f"""
        <div class="minor-kpi nuclear">
            <div class="minor-kpi-title">NUCLEAR</div>
            <div class="minor-kpi-value">
                {metrics['nuclear']}%
            </div>
            <div class="minor-kpi-mwh">
                {format_mwh(metrics['nuclear_mwh'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpiMin_col2:

    st.markdown(
        f"""
        <div class="minor-kpi renewable">
            <div class="minor-kpi-title">RENEWABLE</div>
            <div class="minor-kpi-value">
                {metrics['renewable']}%
            </div>
            <div class="minor-kpi-mwh">
                {format_mwh(metrics['renewable_mwh'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpiMin_col3:

    st.markdown(
        f"""
        <div class="minor-kpi fossil">
            <div class="minor-kpi-title">GAS</div>
            <div class="minor-kpi-value">
                {metrics['fossil']}%
            </div>
            <div class="minor-kpi-mwh">
                {format_mwh(metrics['fossil_mwh'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpiMin_col4:

    st.markdown(
        f"""
        <div class="minor-kpi other">
            <div class="minor-kpi-title">OTHER</div>
            <div class="minor-kpi-value">
                {metrics['other']}%
            </div>
            <div class="minor-kpi-mwh">
                {format_mwh(metrics['other_mwh'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# DAILY GENERATION
# ============================================================

daily_df = get_daily_generation(
    start_date,
    end_date
)

daily_fig = create_generation_chart(
    daily_df
)

st.plotly_chart(
    daily_fig,
    use_container_width=True
)


# ============================================================
# RELATIVE OUTPUT
# ============================================================

relative_df = get_relative_output(
    start_date,
    end_date
)

relative_fig = create_relative_output_chart(
    relative_df
)

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


# ============================================================
# GENERATION MIX
# ============================================================

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


# ============================================================
# DATA SOURCE
# ============================================================

st.divider()

st.subheader("Data Source")

st.write(
    "Generation data is sourced from publicly available electricity "
    "generation data provided by the Independent Electricity System "
    "Operator (IESO)."
)

st.caption(
    f"Data through: {formatted_timestamp}"
)

st.caption(
    "This dashboard is an independent portfolio project and is not "
    "affiliated with or endorsed by the IESO."
)
