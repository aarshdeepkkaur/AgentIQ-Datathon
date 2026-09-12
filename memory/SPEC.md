# AgentIQ — living product spec

## What it does
AgentIQ is a premium dark agricultural intelligence dashboard for monitoring mandi arrivals, modal price vs government MSP, route health, weather impact, and below-MSP risk across a cleaned Datathon baseline.

## Data model
- `mandi_master`: mandi identity, district, state, type, and acreage.
- `mandi_arrivals`: crop/date arrival quantity in quintals, farmer count, and quality flag.
- `price_and_msp`: mandi/crop/date price range, modal price, and MSP.
- `weather_sensors`: IST timestamp, normalized temperature, rainfall, and humidity.
- `transport_logistics`: cleaned route timestamps, warehouse, transit, distance, vehicle, driver, and quality flag.

The MVP uses a typed, local `frontend/src/data/mockData.ts` dataset calibrated to the repository's cleaned outputs. It is labeled `Demo data · API integration pending` and keeps the source schema ready for a future data service.

The live sync enhancement calls `GET /api/data-sync`, which fetches and aggregates the public cleaned CSVs from `aarshdeepkkaur/AgentIQ-Datathon` with a local fallback if GitHub is unavailable. The current crop profile, selected mandi volumes, and warehouse transit values merge live results without blocking first render.

## Key flows
1. Choose a crop from the control center; KPI values, map, hero inspector, insights, charts, and table update.
2. Filter by state, mandi, risk, and search; the registry and insight views update without a page reload.
3. Click an orbit pin or mandi row to update the selected hub inspector.
4. Open Ask AgentIQ from the floating action, sidebar, or footer; submit a suggested or typed question for a clearly labeled mocked response.
5. Use the mobile menu to reach the same dashboard on narrow screens.
6. Toggle Orbit view / Satellite view; both preserve the selected mandi and filtered row set.

## Auth and roles
No authentication or gated roles are present in this demo MVP.

## Enhancements
- KPI strip now has circular Modal Price, Average Transit, and MSP Risk gauges.
- Satellite view uses Leaflet with a demo satellite tile layer and street-map fallback; map coordinates are stable local mandi coordinates because the cleaned repository does not contain latitude/longitude fields.
