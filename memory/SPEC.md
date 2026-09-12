# AgentIQ — living product spec

## What it does
AgentIQ is a premium dark agricultural intelligence dashboard for monitoring mandi arrivals, modal price vs government MSP, route health, weather impact, and below-MSP risk across a cleaned Datathon baseline.

## Data model
- `mandi_master`: mandi identity, district, state, type, and acreage.
- `mandi_arrivals`: crop/date arrival quantity in quintals, farmer count, and quality flag.
- `price_and_msp`: mandi/crop/date price range, modal price, and MSP.
- `weather_sensors`: IST timestamp, normalized temperature, rainfall, and humidity.
- `transport_logistics`: cleaned route timestamps, warehouse, transit, distance, vehicle, driver, and quality flag.

All dashboard figures come from the five real cleaned datasets (no mock data remains). `backend/lib/datasets.py` loads them GitHub-first (`aarshdeepkkaur/AgentIQ-Datathon/data/cleaned`) with the user-uploaded copies bundled in `backend/data/cleaned/` as an offline fallback, cached in memory for 30 minutes. `backend/lib/analytics.py` aggregates them with pandas into `GET /api/dashboard?crop=<name>` (Pydantic models in `backend/models/dashboard.py`, mirrored by `frontend/src/data/types.ts`): per-crop summary (modal, MSP, gap, arrivals, below-MSP %, transit, delay rate, 30-day trend), 57 per-mandi rows (per-mandi price/arrival/transit averages, dominant warehouse, weather on latest arrival day, risk, district-anchored lat/lon), daily/weekly/monthly price trend, weekly weather series, warehouse performance, above/below-MSP distribution, network totals, and data-quality percentages. Crop aliases (Chawal/Basmati/Dhaan→Rice, Makki→Maize, Sarso→Mustard, Narma→Cotton, Ganne→Sugarcane) are merged; only the six real crops are selectable. Unknown crops return 404.

Rainfall↔arrivals correlation is reported two ways: pipeline method (arrival days anchored, missing rain = 0 → ≈0.57) and overlapping-days only (≈0.05). Both are shown in the data-quality footnote and weather chart.

`GET /api/data-sync` (legacy summary endpoint) still exists but the UI and agent no longer depend on it.

## Key flows
1. Choose a crop from the control center; KPI values, map, hero inspector, insights, charts, and table update.
2. Filter by state, mandi, risk, and search; the registry and insight views update without a page reload.
3. Click an orbit pin or mandi row to update the selected hub inspector.
4. Open Ask AgentIQ from the floating action, sidebar, or footer; submit a suggested or typed question for a grounded answer with evidence and an inline mini bar chart.
5. Use the mobile menu to reach the same dashboard on narrow screens.
6. Toggle Orbit view / Satellite view; both preserve the selected mandi and filtered row set.
7. Ask AgentIQ sends the question and selected crop to `POST /api/agent/ask`; the FastAPI route detects crop names and states (Punjab/Haryana/Uttar Pradesh) in the question, routes to msp-risk / route-health / weather-impact / crop-comparison, and answers per-mandi from the full datasets with evidence and `chart` points.
8. Price trend has working D/W/M toggles; the mandi table sorts by any column and paginates 10 rows per page; state/mandi filter options are derived from the data; the loading and error states (with retry) cover the dashboard query.

## Auth and roles
No authentication or gated roles are present in this demo MVP.

## Enhancements
- KPI strip now has circular Modal Price, Average Transit, and MSP Risk gauges.
- Satellite view uses Leaflet with a demo satellite tile layer and street-map fallback; map coordinates are stable local mandi coordinates because the cleaned repository does not contain latitude/longitude fields.
- Ask AgentIQ is now a grounded deterministic FastAPI agent. It routes questions into MSP-risk, route-health, weather-impact, or crop-comparison intents and returns source evidence from the synced data. It does not call an external LLM.
