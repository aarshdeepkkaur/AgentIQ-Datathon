
# 🌾 Mandi-to-Market Supply Chain Optimizer

### AgentIQ-Datathon | Track 3

> An end-to-end data analytics solution that integrates agricultural market data, mandi arrivals, government MSP, weather conditions, and transport logistics into a unified, interactive dashboard.

[![Python](https://img.shields.io/badge/Python-3-blue?logo=python)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-blue?logo=pandas)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Analytics-blue?logo=numpy)](https://numpy.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualization-blue?logo=plotly)](https://plotly.com/python/)

**Team:** Only Arsh

**Team Member:** Arshdeep Kaur

**Repository:** [AgentIQ-Datathon](https://github.com/aarshdeepkkaur/AgentIQ-Datathon)

---

## 📊 Dashboard Preview

<!-- Add a screenshot of your working Streamlit dashboard here -->

![Dashboard Preview](docs/dashboard-preview.png)

The dashboard brings together mandi arrivals, prices, MSP, weather, and transport analytics to help explore agricultural supply chain patterns.

---

## 🎯 1. Problem Statement

Agricultural supply chain data is often distributed across multiple sources, making it difficult to understand mandi arrivals, market prices, government MSP, weather conditions, and transport performance together.

Farmers and other supply chain stakeholders need a clearer view of market trends, price deviations, arrival volumes, and logistics performance.

This project addresses the challenge by integrating five datasets into a unified data cleaning and analytics pipeline, followed by an interactive Streamlit dashboard.

### Key Questions

- Which mandis and crops have the highest arrival volumes?
- How do modal market prices compare with government MSP?
- Which transport routes experience delays?
- Is there a relationship between rainfall and mandi arrival volume?
- How can missing and inconsistent data affect business decisions?

---

## 💡 2. Project Overview

**Mandi-to-Market Supply Chain Optimizer** is a Python-based agricultural supply chain analytics project.

The project consists of two main components:

### 1. Data Cleaning Pipeline

Processes five raw datasets into consistent, analysis-ready CSV files.

The pipeline handles:

- Mixed date and timestamp formats
- Inconsistent measurement units
- Missing and unrecognized values
- Crop-name variations
- Negative and unrealistic values
- Large CSV and Excel files

### 2. Interactive Analytics Dashboard

A Streamlit dashboard that allows users to explore:

- Mandi arrival trends
- Crop-wise arrival distribution
- Modal price vs MSP
- Transport transit performance
- Rainfall and arrival correlation
- Below-MSP records

---

## ✨ 3. Key Features

### 🧹 Data Engineering

- Cleaning pipeline for five raw datasets
- CSV, JSON, and XLSX data ingestion
- Explicit multi-format date parsing
- Unit normalization across datasets
- Missing-value handling using `NaN`
- Data-quality flagging for negative and unrealistic values
- Chunked CSV processing
- Streaming Excel processing using `openpyxl`

### 📈 Analytics

- Total mandi arrival analysis
- Crop-wise arrival distribution
- Top mandis by volume
- Modal price vs MSP comparison
- Below-MSP record analysis
- Average transit time by warehouse
- Transport delay analysis
- Rainfall vs arrival correlation

### 📊 Dashboard

- Interactive Streamlit interface
- Crop, mandi, and date-range filters
- KPI cards
- Line charts
- Bar charts
- Pie chart
- Scatter plot with OLS trendline
- Below-MSP detail table

---

## 🏗️ 4. System Architecture

```text
                ┌──────────────────────────┐
                │      Raw Datasets        │
                │                          │
                │  Mandi Arrivals          │
                │  Mandi Master             │
                │  Price & MSP              │
                │  Transport Logistics      │
                │  Weather Sensors          │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │     Data Ingestion        │
                │                          │
                │  CSV | JSON | XLSX        │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │   Data Cleaning &         │
                │   Validation              │
                │                          │
                │  Date Parsing             │
                │  Unit Normalization       │
                │  Missing Values           │
                │  Quality Flags            │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │    Cleaned CSV Data       │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │  Analytics & Processing   │
                │                          │
                │  Aggregation              │
                │  Price vs MSP             │
                │  Transit Analysis         │
                │  Rainfall Correlation     │
                └────────────┬─────────────┘
                             │
                             ▼
                ┌──────────────────────────┐
                │   Streamlit Dashboard     │
                │                          │
                │  KPIs | Charts | Filters  │
                └──────────────────────────┘
```

---

## 📂 5. Dataset Description

The project uses five synthetic datasets connected through `mandi_id`.

| Dataset | Format | Rows | Description |
|---|---|---:|---|
| `track3_mandi_arrivals.csv` | CSV | 25,000 | Daily crop arrival quantities per mandi, in mixed units |
| `track3_mandi_master.csv` | CSV | 57 | Mandi ID, name, district, state, type, and area |
| `track3_price_and_msp.json` | JSON | 12,000 | Min, max, modal price, and MSP per crop, mandi, and date |
| `track3_transport_logistics.csv` | CSV | 10,400 | Departure/arrival timestamps, distance, vehicle, driver, and warehouse |
| `track3_weather_sensors.xlsx` | XLSX | 15,000 | Temperature, rainfall, and humidity readings with mixed units |

### Data Characteristics

- Synthetic agricultural supply chain data
- Arrivals span approximately January–December 2026
- Multiple date and unit formats
- Crop names with regional variations
- Missing and unrecognized values in some fields

---

## 🧹 6. Data Cleaning & Preprocessing

Data cleaning is a major part of this project because the raw datasets contain inconsistent formats, missing values, and measurement differences.

### Cleaning Operations

| Challenge | Solution |
|---|---|
| Mixed date formats | Explicit date parsing using supported formats |
| Incorrect day/month interpretation | Fixed date-format parsing instead of relying on automatic guessing |
| Mixed arrival units | Convert kg, quintals, and tonnes into quintals |
| Mixed distance units | Convert miles into kilometres |
| Mixed temperature units | Convert Fahrenheit into Celsius |
| Mixed rainfall units | Convert inches into millimetres |
| Missing or unrecognized units | Preserve unusable converted values as `NaN` |
| Negative or unrealistic values | Add quality flags for inspection |
| Large weather Excel file | Stream rows using `openpyxl` |
| Large arrivals CSV | Read data in chunks using Pandas |

### Date Parsing

The transport and weather datasets contain multiple date and timestamp formats.

Instead of relying on automatic date inference, the pipeline uses explicit supported formats and converts unrecognized values into `NaT`.

This reduces the risk of incorrect day/month interpretation and invalid transit-time calculations.

### Unit Normalization

The pipeline standardizes measurements:

- Arrival quantities → Quintals
- Transport distance → Kilometres
- Temperature → Celsius
- Rainfall → Millimetres

This ensures that downstream analysis uses consistent units.

---

## 🧮 7. Missing Value Handling

Missing numerical values are represented using `NaN`.

### What does `NaN` mean?

`NaN` stands for **Not a Number** and is commonly used by Pandas to represent missing or unusable numerical values.

For example:

```text
arrival_quantity_qtl
--------------------
250
NaN
480
```

The `NaN` value does not mean zero arrivals. It means that a valid numerical quantity is unavailable or could not be converted.

### Why do missing values occur?

In this project, missing or unusable arrival quantities may result from:

- Missing units
- Unrecognized units
- Missing numerical values
- Failed unit conversion

### Our Approach

We preserve missing values as `NaN` instead of automatically replacing them with zero.

This is important because:

> Missing arrival data does not necessarily mean that no produce arrived.

The dashboard's total arrival KPI uses valid, non-null quantities only. Therefore, it represents the total quantity successfully parsed from the available data, not a complete estimate of all arrivals.

---

## 📈 8. Analytics & Business Insights

The following results are computed from the cleaned datasets.

### Key Results

| Metric | Result |
|---|---:|
| Total arrivals | ~3.74 million quintals |
| Average modal price | ₹3,797.82 |
| Average MSP | ₹3,719.78 |
| Records below MSP | 40.16% |
| Average transit time | 12.99 hours |
| Delay rate | 0.28% |
| Rainfall-arrivals correlation | 0.54 |

### Detailed Insights

#### 🌾 Total Arrival Volume

Approximately 3.74 million quintals of arrivals were recorded across the year.

This figure is based on successfully parsed, non-null arrival quantities.

#### 💰 Price vs MSP

The average modal price was ₹3,797.82, compared with an average MSP of ₹3,719.78.

Among 9,131 records with both modal price and MSP available, 40.16% had modal prices below MSP.

#### 🏪 Top Mandis by Volume

The top five mandis by arrival volume were:

1. MANDI001
2. MANDI048
3. MANDI050
4. MANDI026
5. MANDI012

Each recorded approximately 72,000–75,000 quintals.

#### 🌾 Crop Distribution

Wheat recorded approximately 629,000 quintals, followed by Maize and Mustard at approximately 520,000 quintals each.

#### 🚚 Transport Performance

The average transit time was 12.99 hours across all warehouses.

The six destination warehouses had average transit times between approximately 12.87 and 13.08 hours.

The delay rate was 0.28% for trips exceeding the 24-hour transit threshold.

#### 🌧️ Rainfall vs Arrivals

The correlation between daily rainfall and daily arrival volume was 0.54 across 275 overlapping days.

This indicates a positive association in the dataset, but correlation does not establish causation.

---

## 📊 9. Dashboard Features

The dashboard is built using Streamlit.

### KPI Cards

- Total arrivals
- Average modal price
- Percentage of records below MSP
- Average transit time

### Visualizations

| Visualization | Purpose |
|---|---|
| Daily arrivals trend | Explore arrival volume over time |
| Modal price vs MSP | Compare market prices with MSP |
| Top 5 mandis | Identify high-volume mandis |
| Crop distribution | Explore crop-wise arrival share |
| Rainfall vs arrivals | Examine the relationship between rainfall and arrivals |
| Transit time by warehouse | Compare warehouse transit performance |
| Below-MSP detail table | Inspect records where modal price is below MSP |

### Interactive Filters

- Crop
- Mandi
- Date range

---

## 🛠️ 10. Tech Stack

| Technology | Purpose |
|---|---|
| Python 3 | Core programming language |
| Pandas | Data cleaning and analysis |
| NumPy | Numerical operations |
| OpenPyXL | Streaming Excel data |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| Statsmodels | OLS trendline support |

### Why These Technologies?

- **Python:** Flexible and widely used for data analytics.
- **Pandas:** Efficient data cleaning, transformation, and aggregation.
- **NumPy:** Numerical operations and missing-value handling.
- **OpenPyXL:** Enables row-wise processing of large Excel files.
- **Streamlit:** Makes it easy to build an interactive analytics dashboard.
- **Plotly:** Provides interactive charts and visual exploration.

---

## 📁 11. Project Structure

```text
project-root/
│
├── data/
│   ├── raw/
│   │   ├── track3_mandi_arrivals.csv
│   │   ├── track3_mandi_master.csv
│   │   ├── track3_price_and_msp.json
│   │   ├── track3_transport_logistics.csv
│   │   └── track3_weather_sensors.xlsx
│   │
│   └── cleaned/
│       ├── mandi_arrivals_cleaned.csv
│       ├── mandi_master_cleaned.csv
│       ├── price_and_msp_cleaned.csv
│       ├── transport_cleaned.csv
│       ├── weather_cleaned.csv
│       ├── top_mandis.csv
│       ├── crop_distribution.csv
│       ├── warehouse_transit.csv
│       ├── daily_arrivals.csv
│       ├── daily_rainfall.csv
│       └── below_msp_by_crop.csv
│
├── notebooks/
│   ├── 01_data_cleaning.py
│   └── 02_analytics.py
│
├── dashboard/
│   └── app.py
│
├── docs/
│   └── dashboard-preview.png
│
├── requirements.txt
├── DATA_DICTIONARY.md
└── README.md
```

---

## 🚀 12. Installation & Setup

### Prerequisites

- Python 3
- Git
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/aarshdeepkkaur/AgentIQ-Datathon.git
cd AgentIQ-Datathon
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Data Cleaning Pipeline

```bash
python notebooks/01_data_cleaning.py
```

This reads the raw datasets from `data/raw/` and writes cleaned CSV files into `data/cleaned/`.

### 5. Run the Analytics Script

```bash
python notebooks/02_analytics.py
```

This generates the precomputed summary CSVs used by the dashboard.

### 6. Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard should be available at:

```text
http://localhost:8501
```

---

## ⚠️ 13. Data Quality & Limitations

### Missing Arrival Quantities

41.6% of arrival records have no usable quantity.

Out of 25,000 arrival records, 10,397 have `arrival_quantity_qtl` as `NaN` after cleaning.

The total arrival KPI therefore represents successfully parsed quantities only.

### Weather Conversion Gaps

Approximately:

- 21% of temperature readings could not be converted.
- 25% of rainfall readings could not be converted.

These gaps are generally caused by missing or unrecognized unit labels.

### Crop Name Aliasing

Some regional crop names were not fully merged into their standard categories.

Examples include:

- Sarso
- Narma
- Ganne
- Makki
- Chawal
- Dhaan

This means some crop-distribution values may be split across aliases instead of being combined into one standard crop category.

### Transit Thresholds

A trip is flagged as delayed when transit time exceeds 24 hours.

A transit time exceeding 168 hours (7 days) is flagged as unrealistic.

These are project-defined thresholds, not domain-validated service-level agreements.

### Synthetic Data

The datasets are synthetic and may contain unrealistic geographic relationships.

For example, a mandi name and location may not correspond to a real-world geographic relationship.

Therefore, the findings should be interpreted as exploratory analytics on the provided dataset, not as verified real-world agricultural market statistics.

### Correlation Limitation

The rainfall-arrivals correlation indicates an association in the data.

It does not prove that rainfall directly causes changes in arrival volume.

---

## 🔮 14. Future Scope

- Integrate mandi master data into the dashboard for more descriptive labels.
- Improve crop-name alias mapping.
- Investigate unrecognized weather units.
- Add a documented source for transit-delay thresholds.
- Integrate the Groq-based summary agent into the dashboard.
- Generate on-demand summaries based on selected dashboard filters.
- Improve data validation and completeness reporting.

---

## 🏆 15. Learning Outcomes

Through this project, we worked on:

- Real-world-style data cleaning challenges
- Handling multiple data formats
- Explicit date parsing
- Unit conversion and normalization
- Missing-value handling
- Data validation and quality flags
- Pandas-based analytics
- Interactive dashboard development
- Business insight generation from data

---

## 👩‍💻 16. Team

### Only Arsh

**Arshdeep Kaur**

Role: Data Cleaning, Analytics, Dashboard Development, and Project Integration

---

## 📜 17. License

This project was developed for the AgentIQ-Datathon.

Add a license here if you choose to publish the project under one.

---

## ⭐ Acknowledgement

Built as part of the **AgentIQ-Datathon**.

Thank you for reviewing our project!