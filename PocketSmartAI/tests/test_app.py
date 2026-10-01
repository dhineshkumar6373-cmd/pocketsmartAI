import os
os.environ["DATABASE_URL"] = "sqlite:///./test_pocketsmart.db"
os.environ["SECRET_KEY"] = "test-secret-key-please-change"
os.environ["AI_ENABLED"] = "false"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
client = TestClient(app)


def register_and_login():
    r = client.post('/api/auth/register', json={"username":"tester","email":"tester@example.com","password":"password123","confirm_password":"password123"})
    assert r.status_code == 200
    r = client.post('/api/auth/login', json={"username":"tester","password":"password123"})
    assert r.status_code == 200


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'


def test_auth_and_home_fallback():
    register_and_login()
    r = client.get('/api/auth/session-info')
    assert r.status_code == 200
    r = client.post('/api/generate-home', json={"total_budget":50000,"num_lights":4,"num_fans":2,"num_furniture":2,"num_dining_tables":1,"living_room":True,"kitchen":True,"bedroom":False,"additional_requirements":"modern"})
    assert r.status_code == 200
    data = r.json()
    assert data['total_budget'] == 50000
    assert data['remaining_budget'] >= 0


def test_party_and_history():
    # Make this test independent from test execution order.
    if client.get("/api/auth/session-info").status_code != 200:
        register_and_login()
    r = client.post('/api/generate-party', json={"total_budget":30000,"num_guests":20,"party_type":"Birthday","venue_type":"Home","needs_catering":True,"needs_decoration":True,"needs_entertainment":True})
    assert r.status_code == 200
    r = client.get('/api/history')
    assert r.status_code == 200
    assert len(r.json()['history']) >= 2


def test_protected_route():
    if client.get("/api/auth/session-info").status_code == 200:
        client.post('/api/auth/logout')
    r = client.post('/api/generate-home', json={"total_budget":10000})
    assert r.status_code == 401
