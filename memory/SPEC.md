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

## Key flows
1. Choose a crop from the control center; KPI values, map, hero inspector, insights, charts, and table update.
2. Filter by state, mandi, risk, and search; the registry and insight views update without a page reload.
3. Click an orbit pin or mandi row to update the selected hub inspector.
4. Open Ask AgentIQ from the floating action, sidebar, or footer; submit a suggested or typed question for a clearly labeled mocked response.
5. Use the mobile menu to reach the same dashboard on narrow screens.

## Auth and roles
No authentication or gated roles are present in this demo MVP.
