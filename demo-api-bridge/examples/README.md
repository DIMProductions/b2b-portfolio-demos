# Examples

## Normal case: legacy payload → new API shape

Request to the Bridge (`POST /bridge/sync`, header `Idempotency-Key: <uuid>`):

```json
{
  "customer_id": "001",
  "full_name": "Taro Yamada",
  "tel": "090-1234-5678",
  "api_key": "secret-key-123"
}
```

`input/mapping_rules.json` drives the transformation (`customer_id → id`, `full_name → name.full`, `tel → phone`) before the Bridge forwards it upstream:

```json
{
  "id": "001",
  "name": {
    "full": "Taro Yamada"
  },
  "phone": "090-1234-5678"
}
```

`api_key` is intentionally dropped by the mapping (never forwarded upstream) and is redacted (`***`) in every log line — see `output/example_logs.jsonl`.

## Error case: upstream retries then succeeds

`src/mock_upstream.py` simulates a flaky upstream that returns `503` on its first two calls, then `200` on the third. The Bridge's `tenacity`-based retry (exponential backoff, max 3 attempts) absorbs this transparently — the caller only ever sees the final `200`. This was verified directly: a live request against the real mock-upstream process showed two `503` responses logged, followed by one `200`, all within a single client-facing call. See `output/success_response.json` / `output/upstream_error.json` for the two possible terminal outcomes (retries exhausted vs. succeeded).

## Idempotency case: same key, no duplicate upstream call

Sending the same request twice with the same `Idempotency-Key` results in the second call hitting Redis and returning the cached response — the mock-upstream process's flaky-failure counter does not advance on the second call, confirming the upstream was never re-invoked.
