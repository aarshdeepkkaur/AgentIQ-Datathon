"""Backend tests for POST /api/agent/ask — grounded FastAPI agent endpoint.

Covers: happy path (non-empty query + crop), validation failure (empty query),
MSP-risk intent, route-health (logistics) intent, and weather-impact intent,
plus per-crop grounding (Maize context differs from Wheat context).
"""

from tests.conftest import api_url


def test_agent_ask_happy_path_returns_grounded_answer(client):
    resp = client.post(
        "/agent/ask",
        json={"query": "tscheck-agent-happy: is wheat above or below MSP?", "crop_name": "Wheat"},
    )
    assert resp.status_code == 200, f"POST {api_url('/agent/ask')} -> {resp.status_code}: {resp.text[:300]}"
    body = resp.json()
    for key in ("answer", "intent", "source", "grounded_at", "evidence"):
        assert key in body, f"missing key {key} in response: {body}"
    assert body["answer"], "answer must be non-empty"
    assert isinstance(body["evidence"], list) and len(body["evidence"]) > 0


def test_agent_ask_empty_query_returns_422(client):
    resp = client.post("/agent/ask", json={"query": "", "crop_name": "Wheat"})
    assert resp.status_code == 422, f"expected 422 for empty query, got {resp.status_code}: {resp.text[:300]}"


def test_agent_ask_msp_risk_grounded_in_synced_metrics(client):
    resp = client.post(
        "/agent/ask",
        json={"query": "tscheck-agent-msp: is wheat below MSP right now?", "crop_name": "Wheat"},
    )
    assert resp.status_code == 200, resp.text[:300]
    body = resp.json()
    assert body["intent"] == "msp-risk", body
    assert "MSP" in body["answer"]
    assert any("below-MSP" in e or "price rows" in e for e in body["evidence"]), body["evidence"]
    assert "price_and_msp_cleaned.csv" in " ".join(body["evidence"])


def test_agent_ask_route_health_from_warehouse_transit(client):
    resp = client.post(
        "/agent/ask",
        json={"query": "tscheck-agent-transit: which warehouse has the slowest transit time?", "crop_name": "Wheat"},
    )
    assert resp.status_code == 200, resp.text[:300]
    body = resp.json()
    assert body["intent"] == "route-health", body
    assert any("Fastest:" in e for e in body["evidence"]), body["evidence"]
    assert any("Slowest:" in e for e in body["evidence"]), body["evidence"]
    assert "warehouse_transit.csv" in " ".join(body["evidence"])


def test_agent_ask_weather_impact_from_cleaned_weather(client):
    resp = client.post(
        "/agent/ask",
        json={"query": "tscheck-agent-weather: how does rainfall affect arrivals?", "crop_name": "Wheat"},
    )
    assert resp.status_code == 200, resp.text[:300]
    body = resp.json()
    assert body["intent"] == "weather-impact", body
    assert "correlation" in body["answer"]
    assert any("correlation" in e for e in body["evidence"]), body["evidence"]
    assert "weather_cleaned.csv" in " ".join(body["evidence"])


def test_agent_ask_uses_selected_crop_context_not_stale_wheat(client):
    wheat_resp = client.post(
        "/agent/ask",
        json={"query": "tscheck-agent-ctx: is it below MSP right now?", "crop_name": "Wheat"},
    )
    maize_resp = client.post(
        "/agent/ask",
        json={"query": "tscheck-agent-ctx: is it below MSP right now?", "crop_name": "Maize"},
    )
    assert wheat_resp.status_code == 200 and maize_resp.status_code == 200
    wheat_body = wheat_resp.json()
    maize_body = maize_resp.json()
    assert wheat_body["answer"].startswith("Wheat"), wheat_body["answer"]
    assert maize_body["answer"].startswith("Maize"), maize_body["answer"]
    assert wheat_body["answer"] != maize_body["answer"]
