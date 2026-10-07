"""
AirScope API Tests
Run: pytest tests/test_api.py -v
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_aqi_city(client):
    r = await client.get("/api/aqi/city?city=Delhi")
    assert r.status_code == 200
    data = r.json()
    assert "aqi" in data
    assert "pollutants" in data


@pytest.mark.asyncio
async def test_aqi_coords(client):
    r = await client.get("/api/aqi/location?lat=28.43&lon=77.0")
    assert r.status_code == 200
    assert r.json()["aqi"] >= 0


@pytest.mark.asyncio
async def test_weather_city(client):
    r = await client.get("/api/weather/city?city=Mumbai")
    assert r.status_code == 200
    data = r.json()
    assert "current" in data
    assert "hourly" in data


@pytest.mark.asyncio
async def test_forecast(client):
    r = await client.get("/api/forecast/city?city=Delhi&days=7")
    assert r.status_code == 200
    data = r.json()
    assert len(data["days"]) == 7
    assert data["model_accuracy"] > 0


@pytest.mark.asyncio
async def test_suggestions(client):
    r = await client.get("/api/suggestions/city?city=Delhi")
    assert r.status_code == 200
    data = r.json()
    assert len(data["suggestions"]) > 0


@pytest.mark.asyncio
async def test_dashboard(client):
    r = await client.get("/api/dashboard?lat=28.43&lon=77.0&city=Sohna")
    assert r.status_code == 200
    data = r.json()
    assert "aqi" in data
    assert "weather" in data
    assert "forecast" in data
    assert "suggestions" in data


@pytest.mark.asyncio
async def test_register_and_login(client):
    # Register
    r = await client.post("/api/auth/register", json={
        "email": "test@airscope.app",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
    })
    assert r.status_code in (201, 400)  # 400 if already exists

    # Login
    r = await client.post("/api/auth/login", json={
        "email": "test@airscope.app",
        "password": "testpassword123",
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_plans_require_auth(client):
    r = await client.get("/api/plans")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_aqi_compare(client):
    r = await client.get("/api/aqi/compare?cities=Delhi,Mumbai,Bangalore")
    assert r.status_code == 200
    data = r.json()
    assert len(data["cities"]) == 3
