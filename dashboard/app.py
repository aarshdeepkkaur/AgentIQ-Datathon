import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Mandi-to-Market Optimizer",
    page_icon="🌾",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    arrivals = pd.read_csv(
        CLEANED_DIR / "mandi_arrivals_cleaned.csv"
    )

    master = pd.read_csv(
        CLEANED_DIR / "mandi_master_cleaned.csv"
    )

    prices = pd.read_csv(
        CLEANED_DIR / "price_and_msp_cleaned.csv"
    )

    transport = pd.read_csv(
        CLEANED_DIR / "transport_cleaned.csv"
    )

    weather = pd.read_csv(
        CLEANED_DIR / "weather_cleaned.csv"
    )

    arrivals["date"] = pd.to_datetime(
        arrivals["date"],
        errors="coerce"
    )

    prices["date"] = pd.to_datetime(
        prices["date"],
        errors="coerce"
    )

    transport["departure_time_clean"] = pd.to_datetime(
        transport["departure_time_clean"],
        errors="coerce"
    )

    weather["timestamp_ist"] = pd.to_datetime(
        weather["timestamp_ist"],
        errors="coerce"
    )

    return (
        arrivals,
        master,
        prices,
        transport,
        weather
    )


arrivals, master, prices, transport, weather = load_data()


# ============================================================
# HEADER
# ============================================================

st.title("🌾 Mandi-to-Market Supply Chain Optimizer")

st.markdown(
    """
    **AgriTech Analytics Dashboard**

    Monitor crop arrivals, mandi prices, MSP comparison,
    transportation efficiency and weather impact.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")

# Crop filter
crops = sorted(
    arrivals["crop_name"]
    .dropna()
    .unique()
)

selected_crop = st.sidebar.selectbox(
    "Select Crop",
    ["All"] + crops
)


# Mandi filter
mandis = sorted(
    arrivals["mandi_id"]
    .dropna()
    .unique()
)

selected_mandi = st.sidebar.selectbox(
    "Select Mandi",
    ["All"] + mandis
)


# Date filter
min_date = arrivals["date"].min().date()
max_date = arrivals["date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_arrivals = arrivals.copy()

filtered_prices = prices.copy()


if selected_crop != "All":

    filtered_arrivals = filtered_arrivals[
        filtered_arrivals["crop_name"]
        == selected_crop
    ]

    filtered_prices = filtered_prices[
        filtered_prices["crop_name"]
        == selected_crop
    ]


if selected_mandi != "All":

    filtered_arrivals = filtered_arrivals[
        filtered_arrivals["mandi_id"]
        == selected_mandi
    ]

    filtered_prices = filtered_prices[
        filtered_prices["mandi_id"]
        == selected_mandi
    ]


if len(selected_dates) == 2:

    start_date = pd.Timestamp(
        selected_dates[0]
    )

    end_date = pd.Timestamp(
        selected_dates[1]
    )

    filtered_arrivals = filtered_arrivals[
        (filtered_arrivals["date"] >= start_date)
        &
        (filtered_arrivals["date"] <= end_date)
    ]

    filtered_prices = filtered_prices[
        (filtered_prices["date"] >= start_date)
        &
        (filtered_prices["date"] <= end_date)
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_arrivals = filtered_arrivals[
    "arrival_quantity_qtl"
].sum()


average_modal = filtered_prices[
    "modal_price"
].mean()


average_msp = filtered_prices[
    "msp"
].mean()


valid_prices = filtered_prices[
    ["modal_price", "msp"]
].dropna()

if len(valid_prices) > 0:

    price_crash_rate = (
        (
            valid_prices["modal_price"]
            < valid_prices["msp"]
        ).mean()
        * 100
    )

else:

    price_crash_rate = 0


average_transit = transport[
    "transit_hours"
].mean()


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "🌾 Total Arrivals",
    f"{total_arrivals:,.0f} Qtl"
)


col2.metric(
    "💰 Avg Modal Price",
    f"₹{average_modal:,.0f}"
)


col3.metric(
    "📉 Price Below MSP",
    f"{price_crash_rate:.1f}%"
)


col4.metric(
    "🚚 Avg Transit Time",
    f"{average_transit:.1f} hrs"
)


st.divider()


# ============================================================
# DAILY ARRIVAL TREND
# ============================================================

st.subheader("📈 Daily Crop Arrival Trend")

daily_arrivals = (
    filtered_arrivals
    .groupby("date")["arrival_quantity_qtl"]
    .sum()
    .reset_index()
)

daily_arrivals.columns = [
    "date",
    "arrivals_qtl"
]

fig_arrivals = px.line(
    daily_arrivals,
    x="date",
    y="arrivals_qtl",
    markers=True,
    title="Daily Arrival Volume"
)

fig_arrivals.update_layout(
    xaxis_title="Date",
    yaxis_title="Arrivals (Quintals)"
)

st.plotly_chart(
    fig_arrivals,
    use_container_width=True
)


# ============================================================
# PRICE VS MSP
# ============================================================

st.subheader("💰 Wholesale Modal Price vs MSP")

price_trend = (
    filtered_prices
    .groupby("date")[
        ["modal_price", "msp"]
    ]
    .mean()
    .reset_index()
)

price_long = price_trend.melt(
    id_vars="date",
    value_vars=[
        "modal_price",
        "msp"
    ],
    var_name="price_type",
    value_name="price"
)

price_long["price_type"] = price_long[
    "price_type"
].replace({
    "modal_price": "Modal Price",
    "msp": "MSP"
})


fig_price = px.line(
    price_long,
    x="date",
    y="price",
    color="price_type",
    markers=True,
    title="Modal Price vs MSP"
)

fig_price.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (₹)"
)

st.plotly_chart(
    fig_price,
    use_container_width=True
)


# ============================================================
# TWO COLUMN SECTION
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# TOP MANDIS
# ============================================================

with col1:

    st.subheader("🏪 Top 5 Mandis by Arrivals")

    top_mandis = (
        filtered_arrivals
        .groupby("mandi_id")[
            "arrival_quantity_qtl"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(5)
        .reset_index()
    )

    fig_mandis = px.bar(
        top_mandis,
        x="mandi_id",
        y="arrival_quantity_qtl",
        title="Top 5 Mandis"
    )

    fig_mandis.update_layout(
        xaxis_title="Mandi",
        yaxis_title="Arrivals (Qtl)"
    )

    st.plotly_chart(
        fig_mandis,
        use_container_width=True
    )


# ============================================================
# CROP DISTRIBUTION
# ============================================================

with col2:

    st.subheader("🌾 Crop-wise Arrival Distribution")

    crop_distribution = (
        filtered_arrivals
        .groupby("crop_name")[
            "arrival_quantity_qtl"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

    fig_crop = px.pie(
        crop_distribution,
        names="crop_name",
        values="arrival_quantity_qtl",
        title="Arrival Distribution by Crop"
    )

    st.plotly_chart(
        fig_crop,
        use_container_width=True
    )


# ============================================================
# WEATHER IMPACT
# ============================================================

st.subheader("🌧️ Rainfall vs Crop Arrivals")

weather["date"] = (
    weather["timestamp_ist"]
    .dt.date
)

daily_rainfall = (
    weather
    .groupby("date")["rainfall_mm"]
    .sum()
    .reset_index()
)

daily_rainfall["date"] = pd.to_datetime(
    daily_rainfall["date"]
)

weather_impact = daily_arrivals.merge(
    daily_rainfall,
    on="date",
    how="inner"
)

if len(weather_impact) > 1:

    correlation = weather_impact[
        [
            "arrivals_qtl",
            "rainfall_mm"
        ]
    ].corr().iloc[0, 1]

    st.metric(
        "Rainfall ↔ Arrival Correlation",
        f"{correlation:.3f}"
    )

    fig_weather = px.scatter(
        weather_impact,
        x="rainfall_mm",
        y="arrivals_qtl",
        trendline="ols",
        title="Rainfall vs Arrival Volume"
    )

    fig_weather.update_layout(
        xaxis_title="Rainfall (mm)",
        yaxis_title="Arrivals (Qtl)"
    )

    st.plotly_chart(
        fig_weather,
        use_container_width=True
    )

else:

    st.warning(
        "Not enough weather data for correlation."
    )


# ============================================================
# TRANSPORTATION
# ============================================================

st.subheader("🚚 Transportation Performance")

warehouse_transit = (
    transport
    .groupby("destination_warehouse")[
        "transit_hours"
    ]
    .mean()
    .sort_values(
        ascending=False
    )
    .reset_index()
)

fig_transport = px.bar(
    warehouse_transit,
    x="destination_warehouse",
    y="transit_hours",
    title="Average Transit Time by Warehouse"
)

fig_transport.update_layout(
    xaxis_title="Warehouse",
    yaxis_title="Average Transit Time (Hours)"
)

st.plotly_chart(
    fig_transport,
    use_container_width=True
)


# ============================================================
# PRICE BELOW MSP TABLE
# ============================================================

st.subheader("🔴 Mandis Where Price Is Below MSP")

below_msp = filtered_prices[
    filtered_prices["modal_price"]
    < filtered_prices["msp"]
].copy()

if len(below_msp) > 0:

    below_msp_table = (
        below_msp[
            [
                "date",
                "mandi_id",
                "crop_name",
                "modal_price",
                "msp"
            ]
        ]
        .sort_values("date")
    )

    st.dataframe(
        below_msp_table,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No price-below-MSP records for the selected filters."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AgentIQ Datathon | Track 3: "
    "Mandi-to-Market Supply Chain Optimizer"
)