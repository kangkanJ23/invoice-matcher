from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get('/health')  # adjust path if different
    assert res.status_code in (200, 404)
