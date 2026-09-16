# Mandi-to-Market Supply Chain Optimizer

**AgentIQ Datathon — Track 3: AgriTech**

An agricultural supply-chain analytics and decision-support system. It cleans five raw mandi datasets into a consistent set of tables, computes arrival, price/MSP, transport and weather analytics over them, and serves the results through a FastAPI backend to a React dashboard with a grounded AI agent.

**Team:** Only Arsh
**Member:** Arshdeep Kaur
**Repository:** https://github.com/aarshdeepkkaur/AgentIQ-Datathon

---

## Architecture

```text
data/raw/  ──▶  notebooks/01_data_cleaning.py  ──▶  data/cleaned/
                                                        │
                                                        ▼
                                        lib/datasets.py + lib/analytics.py
                                                        │
                                                        ▼
                                      FastAPI backend (server.py, /api/*)
                                                        │
                                                        ▼
                                    React/Vite dashboard + AgentIQ chat panel
```

| Layer | Technology | Local address |
| --- | --- | --- |
| Frontend | React 19 + TypeScript + Vite | `http://localhost:3000` |
| Backend | FastAPI + Uvicorn | `http://127.0.0.1:8000` |
| API docs | Swagger UI | `http://127.0.0.1:8000/docs` |
| Persistence | MongoDB (agent chat history) | configured via `.env` |

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`, so the frontend needs no backend URL configuration in development.

---

## Problem Statement

Mandi arrivals, market prices, MSP, weather readings and transport records normally live in separate files with inconsistent units, date formats and crop names. This project consolidates them and makes them queryable, so a user can ask:

- Which mandis and crops have the highest arrival volumes?
- How do modal prices compare against MSP, and which mandis sit below it?
- Where are transport delays concentrated, and which warehouse clears fastest?
- Is there any association between rainfall and arrival volume?
- How much of the data is actually usable after cleaning?

---

## Quick Start

### Prerequisites

| Requirement | Notes |
| --- | --- |
| Python 3.11+ | https://www.python.org/downloads/ |
| Node.js 20+ and npm | https://nodejs.org/ |
| Git | https://git-scm.com/downloads |
| MongoDB | Required. A local install or a free MongoDB Atlas cluster both work. |
| LLM API key | **Optional.** Only needed for the LLM agent mode; see [Using the AI Agent](#using-the-ai-agent). |

### 1. Clone the project

```powershell
git clone https://github.com/aarshdeepkkaur/AgentIQ-Datathon.git
cd AgentIQ-Datathon
```

### 2. Create and activate the virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script with an execution-policy error, either allow scripts for the current session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

or use Command Prompt instead, where activation is:

```bat
venv\Scripts\activate.bat
```

### 3. Install backend dependencies

```powershell
pip install -r requirements.txt
```

`requirements.txt` is a full environment freeze and does not currently list every package the backend imports at runtime. Install the remainder explicitly:

```powershell
pip install motor pymongo openpyxl
```

`motor` and `pymongo` are needed by `lib/db.py`, and `openpyxl` by the weather-sheet step in `notebooks/01_data_cleaning.py`. If `pip` reports an encoding error while reading `requirements.txt`, re-save the file as UTF-8 and retry.

### 4. Create the `.env` file

Create a file named `.env` in the project root. The backend calls `os.environ["MONGO_URL"]` and `os.environ["DB_NAME"]` directly, so **it will not start without these two values**.

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=agentiq
```

Optional variables, all with working defaults if omitted:

```env
CORS_ORIGINS=http://localhost:3000
EMERGENT_LLM_KEY=your_llm_api_key_here
AGENTIQ_DATA_REPO_BASE=https://raw.githubusercontent.com/aarshdeepkkaur/AgentIQ-Datathon/main/data/cleaned
```

`.env` is listed in `.gitignore` and must never be committed. Use your own credentials.

### 5. Run the backend

```powershell
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

| URL | Purpose |
| --- | --- |
| `http://127.0.0.1:8000/api/` | API status check |
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/openapi.json` | OpenAPI specification |

Leave this terminal running.

If you hit OpenBLAS or NumPy thread errors on Windows, set these before starting Uvicorn:

```powershell
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
$env:NUMEXPR_NUM_THREADS="1"
```

### 6. Run the frontend

Open a **second terminal**:

```powershell
cd frontend
npm install
npm run dev
```

The port and the `/api` proxy are already set in `frontend/vite.config.ts`, so no extra flags are needed. Open `http://localhost:3000`.

### Both terminals at a glance

| Terminal | Directory | Command | Purpose |
| --- | --- | --- | --- |
| 1 | Project root | `uvicorn server:app --host 127.0.0.1 --port 8000 --reload` | Backend, APIs, AI agent |
| 2 | `frontend/` | `npm run dev` | React dashboard |

### Frontend scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Start the dev server on port 3000 |
| `npm run build` | Type-check and build for production |
| `npm run preview` | Preview the production build |
| `npm run lint` | Lint with oxlint |
| `npm run typecheck` | Type-check without emitting |

### Regenerating the cleaned data (optional)

`data/cleaned/` is already committed, so the app runs without this step. To rebuild it from the raw files:

```powershell
python notebooks\01_data_cleaning.py
python notebooks\02_analytics.py
```

---

## Using the Dashboard

1. Start the backend, then the frontend, and open `http://localhost:3000`.
2. Pick a crop from the **Tracking crop** selector. Six crops are supported: Wheat, Rice, Maize, Cotton, Mustard and Sugarcane.
3. Narrow the view with the **State**, **Mandi**, **Date window** and **Risk level** filters, or search mandis by name. Filters apply across every panel; **Reset** clears them.
4. Read the KPI strip for headline arrival, price, MSP and transport figures.
5. Explore the central stage, which switches between an orbit view of mandi hubs and a satellite map. Selecting a hub updates the surrounding panels.
6. Review the four insight cards (crop, mandi, logistics, weather) and the analytics charts beneath them.
7. Browse the mandi table and open any row for its detail page at `/mandi/:mandiId`.
8. Check the alerts bell in the header for supply-chain alerts on the current crop and window.
9. Read the data-quality note in the footer — it reports live missing-data percentages for the current payload.
10. Click **Ask AgentIQ** (bottom-right, or in the sidebar and footer) to open the agent chat drawer.

---

## Using the AI Agent

The agent panel opens as a drawer over the dashboard. It sends your question, the selected crop and the active date window to the FastAPI backend, which answers using the cleaned datasets rather than free-form generation.

### Two answering modes

| Mode | When it is used | How it works |
| --- | --- | --- |
| `rules` | Default; always available | Intent detection over the question, then a fixed pandas analysis. Recognised intents include MSP risk, top mandis by modal price, crop comparison, route health and weather impact. |
| `llm` | Only when `EMERGENT_LLM_KEY` is set | An Anthropic Claude model writes a pandas query over the loaded DataFrames, the query runs in a restricted namespace with a timeout, and the model explains the result. |

The LLM mode is **optional**. Without the key, `llm_enabled()` returns false and the agent uses rule-based answers; the LLM path also falls back to rules on any failure. Every response carries a `mode` field so you can see which path produced it.

### Example questions

```text
Show the MSP risk for Wheat only.
Which mandis have records below MSP?
What should farmers do when prices are below MSP?
Show me the transport delay situation.
Which crop has the highest arrival volume?
What is the relationship between rainfall and arrivals?
```

### Request format

From `models/agent.py`. Only `query` is required; `crop_name` defaults to `Wheat`.

```json
{
  "query": "Show the MSP risk for Wheat only. Which mandis have records below MSP and what should farmers do?",
  "crop_name": "Wheat",
  "session_id": "wheat-test-1",
  "date_from": "2026-08-01",
  "date_to": "2026-09-06"
}
```

`query` is capped at 500 characters and `date_from` / `date_to` are `YYYY-MM-DD` strings.

### Testing through Swagger

1. Open `http://127.0.0.1:8000/docs`.
2. Find **POST `/api/agent/ask`**.
3. Click **Try it out**.
4. Paste the JSON above.
5. Click **Execute** and read the response body.

### Testing from PowerShell

```powershell
$body = @{ query = "Which mandis have records below MSP?"; crop_name = "Wheat" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/agent/ask" -Method Post -Body $body -ContentType "application/json"
```

### Streaming endpoint

`POST /api/agent/ask/stream` accepts the same request body and returns Server-Sent Events (`data: <json>` frames). This is the endpoint the dashboard chat drawer actually uses, so answers appear incrementally. `POST /api/agent/ask` returns the same analysis as a single JSON response and is the easier one to test by hand.

---

## API Reference

All routes are mounted under the `/api` prefix.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/` | API status check |
| GET | `/api/dashboard` | Dashboard analytics payload |
| GET | `/api/mandi/{mandi_id}` | Detail for a single mandi |
| GET | `/api/alerts` | Supply-chain alerts |
| GET | `/api/data-sync` | Sync status for the cleaned datasets |
| POST | `/api/agent/ask` | Ask the agent, single JSON response |
| POST | `/api/agent/ask/stream` | Ask the agent, Server-Sent Events |
| GET | `/api/agent/history/{session_id}` | Stored conversation history |
| GET | `/api/status` | Status-check records |
| POST | `/api/status` | Create a status-check record |

`/api/dashboard` and `/api/alerts` accept `crop`, `date_from` and `date_to` query parameters; `/api/dashboard` also accepts `refresh`. An unrecognised crop returns 404 with the list of supported crops.

Full request and response schemas are browsable at `http://127.0.0.1:8000/docs`.

---

## Data Pipeline

`lib/datasets.py` loads the five cleaned CSVs from the GitHub raw URL first and falls back to the bundled copies in `data/cleaned/` when that is unavailable, so the dashboard works offline. The active source is reported in the dashboard footer.

### Cleaning

`notebooks/01_data_cleaning.py` reads `data/raw/` and writes `data/cleaned/`, handling:

- Mixed date and timestamp formats, parsed with explicit format strings
- Mixed units — arrivals to quintals, distance to kilometres, temperature to Celsius, rainfall to millimetres
- CSV, JSON and XLSX inputs, with the large weather workbook streamed row-wise
- Crop-name variations mapped to six canonical names
- Negative arrival quantities and negative transit times, set to `NaN` and flagged (`invalid_negative_quantity`, `invalid_negative_transit`)
- Transit times above 168 hours, treated as unrealistic, set to `NaN` and flagged (`invalid_unrealistic_transit`)
- Missing or unrecognised units, left as `NaN` rather than guessed

### What `NaN` means here

`NaN` means the value is missing or could not be converted. **It does not mean zero.** A missing arrival quantity does not mean no produce arrived at that mandi.

Analytics therefore drop nulls before summing or averaging, which means totals reflect successfully parsed records only and should not be read as complete real-world figures. Roughly 42% of arrival rows have no usable quantity after cleaning, and around 20% of price rows have no MSP; the dashboard footer reports the exact live percentages.

### Datasets

| File | Format | Contents |
| --- | --- | --- |
| `track3_mandi_master.csv` | CSV | 57 mandis: id, name, district, state, type, area |
| `track3_mandi_arrivals.csv` | CSV | Arrival quantities per mandi, crop and date |
| `track3_price_and_msp.json` | JSON | Min, max and modal price plus MSP |
| `track3_transport_logistics.csv` | CSV | Trips with timestamps, distance, vehicle, driver, warehouse |
| `track3_weather_sensors.xlsx` | XLSX | Temperature, rainfall and humidity readings |

Column-level documentation is in [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md). Field notes on the raw files are in `data/raw/track3_dataset_notes.txt`.

---

## Analytics and KPIs

`lib/analytics.py` computes every figure the dashboard and agent display, recalculated against the selected crop and date window on each request.

### Headline KPIs

| Group | Metrics |
| --- | --- |
| Network totals | Total arrivals (qtl), average modal price, average MSP, below-MSP percentage, average transit hours, delay rate, active mandis, record counts per dataset, data date range |
| Crop summary | Modal price, MSP, price gap, arrivals, below-MSP percentage, above/below-MSP record counts, average transit hours, delay rate, trend percentage, season and outlook |
| Per mandi | Modal price, MSP, price gap, arrivals, farmer count, below-MSP percentage, transit hours, delay rate, trip count, destination warehouse, weather, risk level, coordinates |
| Warehouses | Average transit hours, delay rate, trip count and average distance per destination |
| Weather | Average and latest temperature, rainfall and humidity, plus rainfall-to-arrivals correlation |
| Data quality | Percentage of missing arrival quantities, invalid flags, unconverted temperature and rainfall, invalid transit times and missing MSP |

### Series behind the charts

- **Price trend** — modal price, MSP and arrivals at daily, weekly and monthly granularity
- **Weather series** — temperature, rainfall, humidity and arrivals over time
- **MSP distribution** — above- and below-MSP record counts per crop

### Derived classifications

A trip counts as **delayed** when `transit_hours > 24`.

Each mandi is scored into a **risk level** used by the dashboard filter:

| Level | Condition |
| --- | --- |
| High | Price below MSP with at least 50% below-MSP records, or transit above 18 hours |
| Medium | Price below MSP, or at least 40% below-MSP records, or transit above 15 hours |
| Low | Everything else |

Both thresholds are project-defined for this analysis, not industry standards.

### Precomputed summary files

`notebooks/02_analytics.py` writes six standalone summaries into `data/cleaned/` for offline inspection. The live API computes its own figures and does not read these:

```text
top_mandis.csv
crop_distribution.csv
warehouse_transit.csv
daily_arrivals.csv
daily_rainfall.csv
below_msp_by_crop.csv
```

---

## Data Cleaning Evidence

The cleaning pipeline is reproducible: running it against the same raw files always produces the same cleaned output.

- Script: [`notebooks/01_data_cleaning.py`](notebooks/01_data_cleaning.py)
- Raw data: `data/raw/`
- Cleaned data: `data/cleaned/`

### Raw versus cleaned row counts

| Dataset | Raw rows | Cleaned rows | Removed | Reason |
| --- | ---: | ---: | ---: | --- |
| `mandi_master` | 60 | 57 | 3 | Duplicate `mandi_id`, deduplicated |
| `mandi_arrivals` | 25,750 | 25,000 | 750 | Exact duplicate rows, dropped |
| `price_and_msp` | 12,000 | 12,000 | 0 | No deduplication applied |
| `transport_logistics` | 10,400 | 10,000 | 400 | Exact duplicate rows, dropped |
| `weather_sensors` | 15,000 | 15,000 | 0 | No deduplication applied |

No rows are removed for missing or invalid values — those are converted, flagged or set to `NaN` in place, as described above. Only duplicate rows are dropped entirely.

The full breakdown, including how each duplicate count was verified, is in the [Data Cleaning Report](evidence/data_cleaning_report.md). Field-level definitions are in the [Data Dictionary](DATA_DICTIONARY.md).

---

## Project Structure

```text
AgentIQ-Datathon/
├── data/
│   ├── raw/                      # Original Track 3 datasets
│   └── cleaned/                  # Cleaned tables + analytics summaries
├── evidence/
│   └── data_cleaning_report.md   # Raw vs. cleaned row-count breakdown
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/        # KPI strip, charts, map, filters, agent drawer
│   │   │   └── ui/               # Shared UI primitives
│   │   ├── lib/                  # api.ts, queryClient.ts, session.ts, utils
│   │   ├── pages/                # Home.tsx, MandiDetail.tsx
│   │   ├── data/types.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── components.json
│   ├── .oxlintrc.json
│   └── tsconfig*.json
├── lib/
│   ├── agent_llm.py              # Optional LLM-backed agent path
│   ├── agent_rules.py            # Rule-based agent path
│   ├── analytics.py
│   ├── datasets.py
│   ├── db.py
│   └── __init__.py
├── models/                       # Pydantic request/response models
│   ├── agent.py
│   ├── alerts.py
│   ├── dashboard.py
│   ├── data_sync.py
│   ├── mandi.py
│   └── __init__.py
├── notebooks/
│   ├── 01_data_cleaning.py
│   ├── 02_analytics.py
│   └── data_helpers.py
├── routers/                      # FastAPI route modules
│   ├── agent.py
│   ├── alerts.py
│   ├── dashboard.py
│   ├── data_sync.py
│   ├── mandi.py
│   └── __init__.py
├── server.py                     # Backend entry point
├── requirements.txt
├── DATA_DICTIONARY.md
├── transport_sample.csv
├── .gitignore
└── README.md
```

---

## Technology Stack

### Backend

| Technology | Purpose |
| --- | --- |
| Python | Backend and data processing |
| FastAPI | API framework |
| Uvicorn | ASGI server |
| Pandas | Data cleaning and analytics |
| NumPy | Numerical operations |
| OpenPyXL | Excel processing |
| Motor / PyMongo | MongoDB driver for agent chat history |
| httpx | Fetching cleaned datasets over HTTP |
| Pydantic | Request and response validation |
| python-dotenv | Environment configuration |

### Frontend

| Technology | Purpose |
| --- | --- |
| React 19 | UI framework |
| TypeScript | Type safety |
| Vite | Dev server and build tooling |
| Tailwind CSS v4 | Styling |
| TanStack Query | Server-state and data fetching |
| React Router | Routing |
| Recharts | Charts |
| Leaflet / React Leaflet | Map view |
| Motion | Animations |
| Lucide React | Icons |
| Sonner | Toast notifications |
| oxlint | Linting |

---

## Limitations and Data-Quality Notes

- **The datasets are synthetic.** They are Datathon-provided files and may contain unrealistic geographic or market relationships. Treat all findings as exploratory analysis of this dataset, not verified agricultural statistics.
- **No live market data.** Prices and arrivals come from the bundled files; the project does not fetch live mandi prices from any government or market feed.
- **Missing is not zero.** Around 42% of arrival records have no usable quantity after cleaning. Totals cover parsed records only.
- **Correlation is not causation.** The rainfall-to-arrivals correlation describes an association within the data. The weather sensors are also not linked to specific mandis, which further limits interpretation.
- **Thresholds are project-defined.** A trip counts as delayed above 24 transit hours. This is our own choice for this analysis, not an industry service-level agreement.
- **Crop aliasing is partial.** Regional names are mapped onto six canonical crops, so any unmapped alias can split a crop's totals.
- **LLM mode is optional and unverified without a key.** Without `EMERGENT_LLM_KEY`, every answer comes from the rule-based path.
- **MongoDB is required to boot.** Chat history persistence is not optional in the current code.

---

## Team

**Only Arsh** — Arshdeep Kaur
Data cleaning, analytics, backend development, frontend development, AI-agent integration and project assembly.

---

## License

Developed for the AgentIQ Datathon. No license is currently applied.
