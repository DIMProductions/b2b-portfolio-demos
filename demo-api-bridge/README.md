# API Bridge Demo (Enterprise-Grade Connector)

> **概要(日本語)**: 旧形式APIのリクエストを、フィールドマッピング(外部設定ファイル)・リトライ(5xxのみ、指数バックオフ)・タイムアウト・冪等性制御(Redis)・構造化ログ(機密情報は自動マスク)を備えたBridge経由で新形式APIに変換します。単なる中継ではなく、本番投入を想定した堅牢性を実装済み。専用`Dockerfile`でビルドされる実際のデプロイ可能イメージです。起動は `docker-compose up --build` のみ。

This repository demonstrates a production-ready API bridge that safely connects a legacy system to a modern SaaS backend.
It is designed as an independent microservice that absorbs the complexity of integration without requiring changes to your core systems.

## 5-Minute Overview: Data Flow

```text
Legacy API Payload
        ↓ (Idempotency-Key Header)
  Schema Validation (Pydantic: Block 4xx)
        ↓
    Field Mapping (External Config File)
        ↓
  Idempotency Check (Redis: Prevent Duplicates)
        ↓
  Selective Retry & Timeout (Tenacity/httpx: 5xx only)
        ↓
  Structured Logging (Redact Secrets, Correlation ID)
        ↓
     New API (Upstream)
```

## Key Enterprise Features
- **Strict Isolation**: Invalid incoming payloads are rejected immediately, protecting the upstream API.
- **Idempotency**: Duplicate requests (e.g., from network retries by the legacy sender) are safely absorbed by Redis.
- **Resilience**: Temporary upstream failures (5xx, timeouts) are retried with exponential backoff. Client errors (4xx) are NOT retried.
- **Observability**: JSON-structured logging with Correlation IDs and automatic secret redaction.
- **Packaged, not scripted**: The Bridge ships as its own [`Dockerfile`](Dockerfile) — a real deployable image, not just an inline shell command.

## How to Run

1. Start the Bridge, Redis, and Upstream Mock:
```bash
docker-compose up --build
```
2. Check `output/` for example responses and structured logs.

## Acceptance Criteria
See [docs/acceptance_criteria.md](docs/acceptance_criteria.md) for the mechanical definition of done.
