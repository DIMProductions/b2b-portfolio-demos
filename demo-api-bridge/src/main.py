import os
import json
import uuid
import httpx
import logging
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_if_result
import redis.asyncio as redis

# --- Configuration & Logging ---
UPSTREAM_URL = os.getenv("UPSTREAM_URL", "http://localhost:8001/v1/customers")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_bridge")

# --- Schemas ---
class LegacyPayload(BaseModel):
    customer_id: str
    full_name: str
    tel: str
    api_key: str  # Sensitive

app = FastAPI(title="API Bridge Enterprise Connector")

# --- Helpers ---
def redact(payload: dict) -> dict:
    safe = payload.copy()
    if "api_key" in safe: safe["api_key"] = "***"
    return safe

def log_event(req_id: str, level: int, msg: str, **kwargs):
    log_record = {"request_id": req_id, "msg": msg, **kwargs}
    logger.log(level, json.dumps(log_record))

def map_payload(legacy: dict) -> dict:
    with open("input/mapping_rules.json", "r") as f:
        rules = json.load(f)["mappings"]
    new_payload = {"name": {}}
    for old_k, new_k in rules.items():
        if old_k in legacy:
            if "." in new_k:
                parent, child = new_k.split(".")
                new_payload[parent][child] = legacy[old_k]
            else:
                new_payload[new_k] = legacy[old_k]
    return new_payload

def should_retry(resp: httpx.Response) -> bool:
    return resp.status_code >= 500

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=(retry_if_exception_type(httpx.RequestError) | retry_if_result(should_retry))
)
async def send_to_upstream(client: httpx.AsyncClient, payload: dict, req_id: str):
    log_event(req_id, logging.INFO, "Sending to upstream")
    resp = await client.post(UPSTREAM_URL, json=payload, timeout=5.0)
    if resp.status_code >= 500:
        log_event(req_id, logging.WARNING, f"Upstream 5xx error: {resp.status_code}")
    return resp

# --- Endpoints ---
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/bridge/sync")
async def bridge_sync(
    payload: LegacyPayload, 
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    req_id = str(uuid.uuid4())
    log_event(req_id, logging.INFO, "Request received", payload=redact(payload.model_dump()))
    
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
        
    cache_key = f"idem:{idempotency_key}"
    cached = await redis_client.get(cache_key)
    if cached:
        log_event(req_id, logging.INFO, "Idempotency cache hit")
        return json.loads(cached)
        
    new_payload = map_payload(payload.model_dump())
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await send_to_upstream(client, new_payload, req_id)
            
        if 400 <= resp.status_code < 500:
            log_event(req_id, logging.ERROR, "Upstream 4xx Client Error (Not retried)")
            raise HTTPException(status_code=resp.status_code, detail="Upstream validation failed")
            
        if resp.status_code >= 500:
            raise HTTPException(status_code=502, detail="Upstream service unavailable")
            
        result = resp.json()
        await redis_client.setex(cache_key, 3600, json.dumps(result))
        log_event(req_id, logging.INFO, "Success")
        return result
        
    except httpx.RequestError as e:
        log_event(req_id, logging.ERROR, f"Upstream connection error: {str(e)}")
        raise HTTPException(status_code=504, detail="Upstream Gateway Timeout")
