import pytest


def test_data_sync_returns_cleaned_source_and_crop_metrics(client):
    response = client.get('/data-sync')
    assert response.status_code == 200, response.text[:300]
    payload = response.json()
    assert payload['source'] == 'github-cleaned-data'
    assert payload['rows_loaded']['prices'] > 0
    assert len(payload['crop_metrics']) >= 2
    crop = payload['crop_metrics'][0]
    assert {'crop_name', 'arrivals_qtl', 'avg_modal_price', 'avg_msp', 'below_msp_percentage'} <= crop.keys()


def test_data_sync_response_is_usable_when_source_payload_is_present(client):
    response = client.get('/data-sync')
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('top_mandis')
    assert payload.get('warehouse_transit')
