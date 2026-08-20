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

AUTH_HEADER = {"X-Bridge-Auth": main.BRIDGE_API_KEY}


def headers(idempotency_key=None, auth=True):
    h = dict(AUTH_HEADER) if auth else {}
    if idempotency_key:
        h["Idempotency-Key"] = idempotency_key
    return h


@pytest.fixture(autouse=True)
def fresh_redis():
    """Each test gets its own in-memory Redis so idempotency keys never leak across tests."""
    main.redis_client = fakeredis.aioredis.FakeRedis()
    yield


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_missing_idempotency_key():
    response = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers())
    assert response.status_code == 400
    assert "Idempotency-Key" in response.text


@respx.mock(assert_all_called=False)
def test_missing_or_wrong_auth_header_is_rejected():
    route = respx.post(main.UPSTREAM_URL).mock(return_value=httpx.Response(200, json={}))

    no_auth = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers(idempotency_key="auth-key-006", auth=False))
    wrong_auth = client.post(
        "/bridge/sync",
        json=VALID_PAYLOAD,
        headers={"X-Bridge-Auth": "not-the-real-key", "Idempotency-Key": "auth-key-006"},
    )

    assert no_auth.status_code == 401
    assert wrong_auth.status_code == 401
    assert route.call_count == 0  # an unauthenticated caller must never reach upstream


@respx.mock
def test_duplicate_idempotency_key_returns_cached_result():
    route = respx.post(main.UPSTREAM_URL).mock(
        return_value=httpx.Response(200, json={"status": "success", "upstream_id": "001"})
    )
    h = headers(idempotency_key="dup-key-001")

    first = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=h)
    second = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=h)

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

    response = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers(idempotency_key="retry-key-002"))

    assert response.status_code == 200
    assert route.call_count == 3


@respx.mock
def test_upstream_400_is_not_retried():
    route = respx.post(main.UPSTREAM_URL).mock(return_value=httpx.Response(400))

    response = client.post("/bridge/sync", json=VALID_PAYLOAD, headers=headers(idempotency_key="no-retry-key-003"))

    assert response.status_code == 400
    assert route.call_count == 1  # 4xx must not trigger a tenacity retry


@respx.mock(assert_all_called=False)
def test_invalid_payload_never_reaches_upstream():
    route = respx.post(main.UPSTREAM_URL).mock(return_value=httpx.Response(200, json={}))
    incomplete_payload = {"full_name": "Taro Yamada", "tel": "090", "api_key": "sec"}  # missing customer_id

    response = client.post(
        "/bridge/sync", json=incomplete_payload, headers=headers(idempotency_key="invalid-payload-key-004")
    )

    assert response.status_code == 422
    assert route.call_count == 0


@respx.mock
def test_secret_is_not_written_to_logs(caplog):
    respx.post(main.UPSTREAM_URL).mock(
        return_value=httpx.Response(200, json={"status": "success", "upstream_id": "005"})
    )

    with caplog.at_level(logging.INFO):
        response = client.post(
            "/bridge/sync", json=VALID_PAYLOAD, headers=headers(idempotency_key="secret-redact-key-005")
        )

    assert response.status_code == 200
    log_text = "\n".join(caplog.messages)
    assert VALID_PAYLOAD["api_key"] not in log_text
    assert VALID_PAYLOAD["full_name"] not in log_text
    assert VALID_PAYLOAD["tel"] not in log_text
    assert "***" in log_text


def test_unexpected_bug_does_not_leak_payload_or_traceback(monkeypatch, caplog):
    """A future bug in map_payload (or anywhere else in the try block) must
    not turn into a leak: no payload contents, no exception message, no
    traceback in the HTTP response or the logs — just a generic 500."""

    def broken_map_payload(legacy):
        # Simulate a defect whose exception message embeds sensitive data —
        # the worst case for this safety net, not the best case.
        raise KeyError(f"missing mapping for {legacy['full_name']}")

    monkeypatch.setattr(main, "map_payload", broken_map_payload)

    with caplog.at_level(logging.INFO):
        response = client.post(
            "/bridge/sync", json=VALID_PAYLOAD, headers=headers(idempotency_key="crash-key-006")
        )

    assert response.status_code == 500
    assert VALID_PAYLOAD["full_name"] not in response.text
    assert VALID_PAYLOAD["api_key"] not in response.text
    assert "Traceback" not in response.text

    log_text = "\n".join(caplog.messages)
    assert VALID_PAYLOAD["full_name"] not in log_text
