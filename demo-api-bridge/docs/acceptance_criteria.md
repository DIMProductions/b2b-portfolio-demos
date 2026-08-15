# Acceptance Criteria (検収条件)

## PASS Conditions
1. **Schema Validation**: Payloads violating the legacy schema MUST be rejected (422) and MUST NOT be forwarded to the upstream.
2. **Idempotency**: Multiple requests with the same `Idempotency-Key` MUST NOT trigger duplicate upstream requests. The cached response MUST be returned.
3. **Externalized Mapping**: Field mapping logic MUST be read from an external config (`input/mapping_rules.json`) and not hardcoded.
4. **Resilience**: The bridge MUST retry upstream 5xx and Connection Errors up to a configured limit, but MUST NOT retry 4xx errors.
5. **Timeout Constraints**: The bridge MUST abort the upstream request and return a 504 Gateway Timeout if the upstream exceeds the configured time limit.
6. **Log Redaction**: Sensitive fields (e.g., `api_key`, `password`) MUST be redacted or excluded from structured logs.
7. **Test Coverage**: Running `pytest tests/` MUST result in a 100% PASS rate.
8. **Reproducibility**: The entire environment (Bridge, Redis, Upstream Mock) MUST be reproducible purely via `docker-compose up`.

## Out of Scope (除外事項)
* **Complex Message Brokers**: Kafka, RabbitMQ, or complex Dead Letter Queues (DLQ) are not included to keep the module strictly decoupled.
* **Authentication Provider**: The bridge relies on standard headers; it does not issue OAuth tokens itself.
