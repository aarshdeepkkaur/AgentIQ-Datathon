"""GET /api/dashboard aggregates the five cleaned datasets for a crop."""

CROPS = ["Wheat", "Rice", "Maize", "Cotton", "Mustard", "Sugarcane"]


def test_dashboard_wheat_matches_pipeline_baseline(client):
    resp = client.get("/dashboard", params={"crop": "Wheat"})
    assert resp.status_code == 200, resp.text[:300]
    body = resp.json()
    assert body["selected_crop"] == "Wheat"
    assert body["crops"] == CROPS
    assert len(body["mandis"]) == 57
    totals = body["totals"]
    assert abs(totals["total_arrivals_qtl"] - 3_735_652) < 1_000
    assert abs(totals["avg_modal_price"] - 3797.82) < 0.5
    assert abs(totals["avg_msp"] - 3719.78) < 0.5
    assert abs(totals["below_msp_percentage"] - 40.16) < 0.2
    assert abs(totals["avg_transit_hours"] - 12.99) < 0.05
    assert abs(body["data_quality"]["arrivals_missing_quantity_pct"] - 41.6) < 0.2
    assert body["price_trend"]["monthly"] and body["price_trend"]["weekly"] and body["price_trend"]["daily"]
    assert {w["destination_warehouse"] for w in body["warehouses"]} >= {"WH-NORTH", "WH-SOUTH", "EXPORT-TERMINAL"}
    assert [m["crop_name"] for m in body["msp_distribution"]] == CROPS


def test_dashboard_merges_crop_aliases_into_canonical_crop(client):
    resp = client.get("/dashboard", params={"crop": "Makki"})
    assert resp.status_code == 200
    assert resp.json()["selected_crop"] == "Maize"


def test_dashboard_rejects_unknown_crop(client):
    resp = client.get("/dashboard", params={"crop": "Soybean"})
    assert resp.status_code == 404
    assert "Soybean" in resp.json()["detail"]


def test_dashboard_mandi_rows_have_risk_and_geo(client):
    body = client.get("/dashboard", params={"crop": "Rice"}).json()
    rows = body["mandis"]
    assert all(row["risk"] in {"low", "medium", "high"} for row in rows)
    assert all(26 < row["latitude"] < 33 and 73 < row["longitude"] < 81 for row in rows)
    assert rows == sorted(rows, key=lambda row: row["arrival_quantity_qtl"], reverse=True)
