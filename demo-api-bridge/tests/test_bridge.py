import pytest
from fastapi.testclient import TestClient
from src.main import app

# Using TestClient for synchronous API testing
client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

# Additional pytest cases would mock Redis and httpx here.
# For demo brevity, we just prove the test framework is wired up.
def test_missing_idempotency_key():
    payload = {"customer_id": "001", "full_name": "Taro", "tel": "090", "api_key": "sec"}
    response = client.post("/bridge/sync", json=payload)
    assert response.status_code == 400
    assert "Idempotency-Key" in response.text
