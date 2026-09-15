====================================================================
 MANDI-TO-MARKET SUPPLY CHAIN OPTIMIZER
 AgentIQ Datathon - Track 3: AgriTech
====================================================================

An end-to-end agricultural supply chain analytics and decision-support
system. It brings together mandi arrivals, market prices, government
MSP data, weather conditions, and transport logistics into a single
pipeline, exposes the results through a FastAPI backend, and presents
them through an interactive React dashboard with a built-in AI agent.

Built with: Python, FastAPI, React, Vite, Pandas, NumPy, Recharts

Team: Only Arsh
Member: Arshdeep Kaur
Repository: https://github.com/aarshdeepkkaur/AgentIQ-Datathon

--------------------------------------------------------------------
 OVERVIEW
--------------------------------------------------------------------

The application is split into a React/Vite frontend and a FastAPI
backend that communicate over HTTP.

  Component              Purpose                          Local Address
  ----------------------------------------------------------------------
  React/Vite frontend     Dashboard and AI-agent UI        http://localhost:3000
  FastAPI backend         APIs, analytics, agent logic     http://127.0.0.1:8000
  Swagger docs            API testing and reference        http://127.0.0.1:8000/docs

It's built to help farmers and other supply-chain stakeholders make
sense of mandi arrivals, prices, MSP, weather, and transport data -
all of which is usually scattered across separate sources.

--------------------------------------------------------------------
 1. PROBLEM STATEMENT
--------------------------------------------------------------------

Agricultural supply chain data is fragmented by nature: arrivals,
prices, MSP, weather, and transport records rarely live in one
place, which makes it hard to see the full picture.

This project pulls five agricultural datasets into a single
cleaning-and-analytics pipeline, then surfaces the results through a
FastAPI backend, a React dashboard, and an AI agent - with the goal
of answering questions such as:

  - Which mandis and crops see the highest arrival volumes?
  - How do modal market prices compare against government MSP?
  - Which mandis have records below MSP in the available data?
  - Where are transport delays occurring?
  - Is there any relationship between rainfall and arrival volume?
  - How should missing or inconsistent data be accounted for in
    these decisions?
  - What actionable steps can farmers take based on what the data
    shows?

--------------------------------------------------------------------
 2. PROJECT OVERVIEW
--------------------------------------------------------------------

Mandi-to-Market Supply Chain Optimizer is a Python-based analytics
and decision-support project built around four layers:

Data cleaning pipeline - turns raw, inconsistent agricultural
datasets into analysis-ready files. It handles mixed date and
timestamp formats, inconsistent units, missing or unrecognized
values, crop-name variations, negative/unrealistic values, and
large CSV/Excel files, while flagging data-quality issues along the
way.

Analytics layer - computes arrival totals, crop-wise distributions,
top mandis by volume, modal price vs. MSP comparisons, below-MSP
records, transport transit performance, warehouse summaries, and
rainfall-arrival patterns.

FastAPI backend - exposes this data through routes for the
dashboard, mandi lookups, alerts, data sync, and AI-agent queries.

React/Vite frontend - an interactive dashboard with charts, filters,
mandi/crop insights, and a conversational AI-agent panel, all wired
to the backend APIs.

--------------------------------------------------------------------
 3. KEY FEATURES
--------------------------------------------------------------------

Data engineering:
  - Cleaning pipeline for five raw datasets
  - CSV, JSON, and XLSX ingestion
  - Explicit multi-format date parsing
  - Unit normalization across datasets
  - Missing-value handling via NaN
  - Data-quality flagging and negative-value validation
  - Chunked CSV processing and streaming Excel reads via openpyxl

Analytics:
  - Total and crop-wise arrival analysis
  - Top mandis by volume
  - Modal price vs. MSP comparison, including below-MSP analysis
  - Average transit time by warehouse and transport delay analysis
  - Rainfall vs. arrival analysis

FastAPI backend:
  - Modular API routes (dashboard, mandi, alerts, data sync, agent)
  - Swagger documentation
  - Structured request/response models

AI agent:
  - Handles natural-language agricultural questions
  - MSP-risk and below-MSP mandi analysis
  - Rule-based reasoning, with optional Groq-based LLM support
  - Data-backed, farmer-oriented recommendations

React/Vite dashboard:
  - Crop-based filtering and API-connected charts
  - KPI cards and supply-chain analytics views
  - AI-agent chat interface
  - Built with Recharts, Framer Motion, and Lucide React

--------------------------------------------------------------------
 4. SYSTEM ARCHITECTURE
--------------------------------------------------------------------

                         +--------------------------+
                         |      Raw Datasets        |
                         |                          |
                         |  Mandi Arrivals          |
                         |  Mandi Master            |
                         |  Price & MSP             |
                         |  Transport Logistics     |
                         |  Weather Sensors         |
                         +------------+-------------+
                                      |
                                      v
                         +--------------------------+
                         |   Data Cleaning Pipeline |
                         |                          |
                         |  Date Parsing            |
                         |  Unit Normalization      |
                         |  Missing Values          |
                         |  Data Quality Flags      |
                         +------------+-------------+
                                      |
                                      v
                         +--------------------------+
                         |     Cleaned CSV Data      |
                         |       data/cleaned/       |
                         +------------+-------------+
                                      |
                                      v
                         +--------------------------+
                         |   Analytics and Dataset   |
                         |       Processing          |
                         +------------+-------------+
                                      |
                                      v
                         +--------------------------+
                         |      FastAPI Backend      |
                         |       Port 8000           |
                         |                          |
                         |  Dashboard APIs           |
                         |  Mandi APIs               |
                         |  Alert APIs               |
                         |  Data Sync APIs           |
                         |  AI Agent APIs            |
                         +------------+-------------+
                                      |
                                      v
                         +--------------------------+
                         |    React/Vite Frontend    |
                         |       Port 3000           |
                         |                          |
                         |  KPIs | Charts | Filters  |
                         |  AI Agent | Insights      |
                         +--------------------------+

--------------------------------------------------------------------
 5. AI AGENT ARCHITECTURE
--------------------------------------------------------------------

The agent lets users ask supply-chain questions in plain language,
for example:

  Show the MSP risk for Wheat only.
  Which mandis are below MSP?
  What should farmers do when prices are below MSP?
  Show me the transport delay situation.

Request flow:

  User Question
        |
        v
  React Frontend
        |
        v
  FastAPI Agent Route
        |
        v
  Question / Intent Detection
        |
        +------------------------+
        v                        v
  Rule-Based Analysis       Optional LLM
        |                      Support
        +-----------+------------+
                    v
          Data-Backed Agent Answer
                    |
                    v
             React Frontend

The agent's core files:

  lib/agent_llm.py
  lib/agent_rules.py
  models/agent.py
  routers/agent.py

The current implementation supports rule-based analysis over the
cleaned data, with optional Groq-based LLM support.

--------------------------------------------------------------------
 6. DATASET DESCRIPTION
--------------------------------------------------------------------

Five synthetic datasets, linked through mandi-related identifiers:

  Dataset                            Format   Rows     Description
  ----------------------------------------------------------------------
  track3_mandi_arrivals.csv          CSV      25,000   Crop arrival
                                                         quantities per
                                                         mandi, mixed units
  track3_mandi_master.csv            CSV      57       Mandi ID, name,
                                                         district, state,
                                                         type, area
  track3_price_and_msp.json          JSON     12,000   Min, max, modal
                                                         price, plus MSP
  track3_transport_logistics.csv     CSV      10,400   Transport
                                                         timestamps,
                                                         distance,
                                                         vehicle, driver,
                                                         warehouse
  track3_weather_sensors.xlsx        XLSX     15,000   Temperature,
                                                         rainfall,
                                                         humidity

The data is synthetic and intentionally messy: mixed date/timestamp
formats, inconsistent units, crop-name variants, missing values, and
varying quality across datasets.

--------------------------------------------------------------------
 7. DATA CLEANING AND PREPROCESSING
--------------------------------------------------------------------

The cleaning script:

  notebooks/01_data_cleaning.py

It reads from data/raw/ and writes cleaned output to data/cleaned/.

  Challenge                            Solution
  ----------------------------------------------------------------------
  Mixed date formats                   Explicit date parsing using
                                        supported formats
  Incorrect day/month interpretation   Explicit format handling
  Mixed arrival units                  Convert kg, quintals, tonnes
                                        into quintals
  Mixed distance units                 Convert miles into kilometres
  Mixed temperature units              Convert Fahrenheit into Celsius
  Mixed rainfall units                 Convert inches into millimetres
  Missing/unrecognized units           Preserve unconverted values
                                        as NaN
  Negative values                      Flag for inspection
  Large weather Excel file             Stream rows using openpyxl
  Large arrivals CSV                   Read in chunks using Pandas

Unit normalization standardizes arrival quantities to quintals,
distance to kilometres, temperature to Celsius, and rainfall to
millimetres, so downstream analytics work off consistent units.

Data quality checks flag negative arrival quantities, negative
transit times, missing units, missing weather measurements, and
unrecognized conversion units - while keeping the raw datasets
untouched and separate from the cleaned output.

--------------------------------------------------------------------
 8. MISSING VALUE HANDLING
--------------------------------------------------------------------

Missing numerical values are represented as NaN rather than being
filled in with zero.

  arrival_quantity_qtl
  --------------------
  250
  NaN
  480

NaN here means the value is unavailable or couldn't be converted -
not that arrivals were zero. This distinction matters: missing
arrival data does not mean no produce arrived.

Common causes include missing or unrecognized units, missing
numerical values, failed unit conversion, and incomplete source
records. Analytics that use numerical quantities operate only on
valid, non-null values, so calculated totals reflect successfully
parsed data and shouldn't be read as complete real-world totals.

--------------------------------------------------------------------
 9. ANALYTICS AND BUSINESS INSIGHTS
--------------------------------------------------------------------

Core analytics logic lives in lib/analytics.py, with additional
processing in notebooks/02_analytics.py. It produces:

  - Total and crop-wise arrival volume
  - Top mandis by volume
  - Average modal price and average MSP
  - Records below MSP
  - Average transit time and delayed transport trips
  - Daily rainfall and arrival trends
  - Warehouse transit performance

Generated files:

  data/cleaned/below_msp_by_crop.csv
  data/cleaned/crop_distribution.csv
  data/cleaned/daily_arrivals.csv
  data/cleaned/daily_rainfall.csv
  data/cleaned/top_mandis.csv
  data/cleaned/warehouse_transit.csv

--------------------------------------------------------------------
 10. FASTAPI BACKEND
--------------------------------------------------------------------

Entry point: server.py

The backend is built with FastAPI and uses a main /api router
prefix. Routes are organized under routers/:

  routers/agent.py
  routers/alerts.py
  routers/dashboard.py
  routers/data_sync.py
  routers/mandi.py

Request/response models live under models/. Supporting logic is in:

  lib/datasets.py
  lib/analytics.py
  lib/db.py
  lib/agent_rules.py
  lib/agent_llm.py

The backend reads and processes cleaned data, runs analytics, serves
structured responses to the React dashboard, provides mandi and alert
information, supports AI-agent queries, and connects the frontend to
the underlying data and agent logic.

  Backend: http://127.0.0.1:8000
  Docs:    http://127.0.0.1:8000/docs

### API Routes

The main API prefix is:

  /api

Available routes:

  GET     /api/
          Basic API root response

  POST    /api/status
          Create/store a status check

  GET     /api/status
          Get status checks

  POST    /api/agent/ask
          Ask the AI agent a natural-language question

  POST    /api/agent/ask/stream
          Ask the AI agent and receive a streamed response

  GET     /api/agent/history/{session_id}
          Get conversation history for a session

  GET     /api/alerts
          Get supply-chain alerts

  GET     /api/dashboard
          Get dashboard analytics and KPI data

  GET     /api/data_sync
          Get data synchronization information

  GET     /api/mandi/{mandi_id}
          Get details for a specific mandi

Interactive API documentation:

  http://127.0.0.1:8000/docs

OpenAPI specification:

  http://127.0.0.1:8000/openapi.json

--------------------------------------------------------------------
 11. REACT/VITE FRONTEND
--------------------------------------------------------------------

Located in frontend/, built with React, Vite, Recharts, Framer
Motion, and Lucide React.

It handles dashboard KPIs, charts and analytics views, crop-based
filtering, mandi information, the AI-agent interface, and all API
communication with the backend.

Commands:

  npm run dev -- --port 3000     start dev server
  npm run build                  production build
  npm run lint                   lint
  npm run preview                preview production build

Frontend address: http://localhost:3000

--------------------------------------------------------------------
 12. PROJECT STRUCTURE
--------------------------------------------------------------------

AgentIQ-Datathon/
|
|-- data/
|   |-- raw/
|   |   `-- Original agricultural datasets
|   |
|   `-- cleaned/
|       |-- mandi_arrivals_cleaned.csv
|       |-- mandi_master_cleaned.csv
|       |-- price_and_msp_cleaned.csv
|       |-- transport_cleaned.csv
|       |-- weather_cleaned.csv
|       |-- below_msp_by_crop.csv
|       |-- crop_distribution.csv
|       |-- daily_arrivals.csv
|       |-- daily_rainfall.csv
|       |-- top_mandis.csv
|       `-- warehouse_transit.csv
|
|-- frontend/
|   |-- package.json
|   |-- package-lock.json
|   |-- vite.config.js
|   |-- index.html
|   |-- eslint.config.js
|   `-- src/
|       `-- React frontend source files
|
|-- lib/
|   |-- agent_llm.py
|   |-- agent_rules.py
|   |-- analytics.py
|   |-- datasets.py
|   |-- db.py
|   `-- __init__.py
|
|-- models/
|   |-- agent.py
|   |-- alerts.py
|   |-- dashboard.py
|   |-- data_sync.py
|   |-- mandi.py
|   `-- __init__.py
|
|-- notebooks/
|   |-- 01_data_cleaning.py
|   |-- 02_analytics.py
|   `-- data_helpers.py
|
|-- routers/
|   |-- agent.py
|   |-- alerts.py
|   |-- dashboard.py
|   |-- data_sync.py
|   |-- mandi.py
|   `-- __init__.py
|
|-- server.py
|-- requirements.txt
|-- DATA_DICTIONARY.md
|-- test_groq.py
|-- transport_sample.csv
|-- .env
|-- .gitignore
`-- README.md

--------------------------------------------------------------------
 13. INSTALLATION AND SETUP
--------------------------------------------------------------------

Prerequisites: Python 3, Node.js and npm, Git, and pip.

1) Clone the repository

  git clone https://github.com/aarshdeepkkaur/AgentIQ-Datathon.git
  cd AgentIQ-Datathon

2) Create and activate a virtual environment

  Windows:
    python -m venv venv
    .\venv\Scripts\Activate.ps1

  Linux/macOS:
    python -m venv venv
    source venv/bin/activate

3) Install backend dependencies

  pip install -r requirements.txt

4) Install frontend dependencies

  cd frontend
  npm install

5) Run the data cleaning pipeline

  From the project root:
    python notebooks\01_data_cleaning.py

  This reads raw datasets from data/raw/ and writes cleaned files to
  data/cleaned/.

6) Run the analytics script

  python notebooks\02_analytics.py

  This generates the summary files used by the analytics and
  dashboard layers.

7) Start the FastAPI backend

  In a terminal:
    cd D:\AgentIQ-Datathon
    .\venv\Scripts\Activate.ps1

  Set the numerical-library thread variables:
    $env:OPENBLAS_NUM_THREADS="1"
    $env:OMP_NUM_THREADS="1"
    $env:MKL_NUM_THREADS="1"
    $env:NUMEXPR_NUM_THREADS="1"

  Start the server:
    uvicorn server:app --host 127.0.0.1 --port 8000 --reload

  Backend:     http://127.0.0.1:8000
  Swagger:     http://127.0.0.1:8000/docs

  Keep this terminal running.

8) Start the React/Vite frontend

  In a second terminal:
    cd D:\AgentIQ-Datathon\frontend
    npm run dev -- --port 3000

  Frontend: http://localhost:3000, communicating with the backend
  on port 8000.

--------------------------------------------------------------------
 14. API TESTING
--------------------------------------------------------------------

The FastAPI backend can be tested through the Swagger UI:

  http://127.0.0.1:8000/docs

### AI-Agent Request

The AI-agent endpoint is:

  POST /api/agent/ask

It accepts a natural-language query and related parameters, as
defined in models/agent.py.

Example request:

```json
{
  "query": "Show the MSP risk for Wheat only. Which mandis have records below MSP and what should farmers do?",
  "crop_name": "Wheat",
  "session_id": "wheat-test-1",
  "date_from": "2026-08-01",
  "date_to": "2026-09-06"
}

--------------------------------------------------------------------
 15. TECHNOLOGY STACK
--------------------------------------------------------------------

  Technology       Purpose
  ----------------------------------------------------------------
  Python           Backend and data-processing language
  FastAPI          Backend API framework
  Uvicorn          ASGI server
  Pandas           Data cleaning and analysis
  NumPy            Numerical operations
  OpenPyXL         Excel processing
  Plotly           Analytics visualization support
  Statsmodels      Statistical trendline support
  React            Frontend user interface
  Vite             Frontend development and build tool
  Recharts         React charts
  Framer Motion    Frontend animations
  Lucide React     Frontend icons
  Groq             Optional LLM support for the AI agent

Python and Pandas/NumPy were chosen for their strength in data
cleaning and numerical work; FastAPI for fast, well-documented APIs;
and React with Vite for a responsive, component-based frontend with
a quick development loop. OpenPyXL enables row-wise streaming of the
large weather Excel file, Recharts handles the dashboard's charts,
and Groq provides optional LLM-backed responses for the AI agent.

--------------------------------------------------------------------
 16. DATA DICTIONARY
--------------------------------------------------------------------

Column-level documentation for the raw and cleaned datasets is in
DATA_DICTIONARY.md.

--------------------------------------------------------------------
 17. DATA QUALITY AND LIMITATIONS
--------------------------------------------------------------------

Missing arrival quantities - Some records lack usable quantities due
to missing values or units. The total arrival KPI reflects
successfully parsed quantities only.

Weather conversion gaps - Temperature and rainfall values stay
missing (rather than being guessed at) when the source unit is
absent or unrecognized.

Crop name aliasing - Some regional crop names (Sarso, Narma, Ganne,
Makki, Chawal, Dhaan, among others) may not be fully merged into
standard categories, which can split crop-distribution values across
aliases.

Transit thresholds - A trip is flagged as delayed past 24 hours, and
transit times over 168 hours are treated as unrealistic for
data-quality review. These thresholds are project-defined, not
verified industry SLAs.

Synthetic data - The datasets are synthetic and may contain
unrealistic geographic or market relationships. The current version
does not fetch live mandi prices or live market data. Findings should
be read as exploratory analytics on this dataset, not as verified
real-world agricultural statistics.

Correlation, not causation - The rainfall-arrivals relationship
reflects an association in the data, not a proven causal effect.

--------------------------------------------------------------------
 18. FUTURE SCOPE
--------------------------------------------------------------------

  - Integrate live mandi and market-price data
  - Add real-time data synchronization
  - Improve crop-name alias mapping and missing-data reporting
  - Add crop-price forecasting and weather-based risk prediction
  - Improve transport route optimization and add warehouse
    recommendations
  - Add multilingual and voice-based AI-agent interaction
  - Improve farmer-specific recommendations
  - Deploy to cloud infrastructure
  - Add authentication and user-specific dashboards
  - Add automated alerts for price crashes and transport delays

--------------------------------------------------------------------
 19. LEARNING OUTCOMES
--------------------------------------------------------------------

This project involved working through real-world-style data cleaning
challenges: handling multiple formats, explicit date parsing, unit
conversion, missing-value handling, and data validation with quality
flags. On top of that, it covered Pandas-based analytics, FastAPI
backend development and API design, a full React/Vite frontend with
interactive charts, AI-agent integration, and tying all of these
pieces together into one working system.

--------------------------------------------------------------------
 20. TEAM
--------------------------------------------------------------------

Only Arsh - Arshdeep Kaur
Role: data cleaning, analytics, backend development, frontend
development, AI-agent integration, and overall project integration.

--------------------------------------------------------------------
 21. LICENSE
--------------------------------------------------------------------

Developed for the AgentIQ Datathon. Add a license here if you choose
to publish the project under one.

--------------------------------------------------------------------
 ACKNOWLEDGEMENT
--------------------------------------------------------------------

Built as part of the AgentIQ Datathon. Thanks for taking the time to
review it.