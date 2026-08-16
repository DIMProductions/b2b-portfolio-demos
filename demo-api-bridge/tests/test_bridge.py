import logging

import fakeredis.aioredis
import httpx
import pytest
import respx
from fastapi.testclient import TestClient

import src.main as main

client = TestClient(main.app)

VALID_PAYLOAD = {
    "customer_id": "001",
    "full_name": "Taro Yamada",
    "tel": "090-1234-5678",
    "api_key": "top-secret-value",
}


@pytest.fixture(autouse=True)
def fresh_redis():
    """Each test gets its own in-memory Redis so idempotency keys never leak across tests."""
    main.redis_client = fakeredis.aioredis.FakeRedis()
    yield


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_missing_idempotency_key():
    response = client.post("/bridge/sync", json=VALID_PAYLOAD)
    assert response.status_code == 400
    assert "Idempotency-Key" in response.text


@respx.mock
def test_duplicate_idempotency_key_returns_cached_result():
    route = respx.post(main.UPSTREAM_URL).mock(
        return_value=httpx.Response(200, json={"status": "success", "upstream_id": "001"})
    )
    headers = {"Idempotency-Key": "dup-key-001"}

    first = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers)
    second = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert route.call_count == 1  # second call must be served from the idempotency cache


@respx.mock
def test_upstream_500_is_retried():
    route = respx.post(main.UPSTREAM_URL).mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(500),
            httpx.Response(200, json={"status": "success", "upstream_id": "002"}),
        ]
    )
    headers = {"Idempotency-Key": "retry-key-002"}

    response = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers)

    assert response.status_code == 200
    assert route.call_count == 3


@respx.mock
def test_upstream_400_is_not_retried():
    route = respx.post(main.UPSTREAM_URL).mock(return_value=httpx.Response(400))
    headers = {"Idempotency-Key": "no-retry-key-003"}

    response = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers)

    assert response.status_code == 400
    assert route.call_count == 1  # 4xx must not trigger a tenacity retry


@respx.mock(assert_all_called=False)
def test_invalid_payload_never_reaches_upstream():
    route = respx.post(main.UPSTREAM_URL).mock(return_value=httpx.Response(200, json={}))
    incomplete_payload = {"full_name": "Taro Yamada", "tel": "090", "api_key": "sec"}  # missing customer_id
    headers = {"Idempotency-Key": "invalid-payload-key-004"}

    response = client.post("/bridge/sync", json=incomplete_payload, headers=headers)

    assert response.status_code == 422
    assert route.call_count == 0


@respx.mock
def test_secret_is_not_written_to_logs(caplog):
    respx.post(main.UPSTREAM_URL).mock(
        return_value=httpx.Response(200, json={"status": "success", "upstream_id": "005"})
    )
    headers = {"Idempotency-Key": "secret-redact-key-005"}

    with caplog.at_level(logging.INFO):
        response = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers)

    assert response.status_code == 200
    log_text = "\n".join(caplog.messages)
    assert VALID_PAYLOAD["api_key"] not in log_text
    assert "***" in log_text
