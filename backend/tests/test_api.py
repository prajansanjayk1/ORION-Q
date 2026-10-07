from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoints():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    res_data = client.get("/api/v1/health/data")
    assert res_data.status_code == 200
    assert res_data.json()["provider_adapter"] == "ACTIVE"


def test_market_session_endpoint():
    res = client.get("/api/v1/market-session?mode=AUTO")
    assert res.status_code == 200
    data = res.json()
    assert "active_market" in data
    assert "india_session" in data
    assert "us_session" in data


def test_supported_markets_endpoint():
    res = client.get("/api/v1/markets")
    assert res.status_code == 200
    data = res.json()
    assert "supported_modes" in data
