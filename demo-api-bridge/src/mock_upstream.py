from fastapi import FastAPI, Request, HTTPException
import asyncio
import json

app = FastAPI(title="Mock Upstream API")
failure_count = 0

@app.post("/v1/customers")
async def create_customer(request: Request):
    global failure_count
    data = await request.json()
    
    # Simulate a flaky upstream (fails first 2 times, then succeeds)
    # This demonstrates the retry logic in the bridge
    if failure_count < 2:
        failure_count += 1
        raise HTTPException(status_code=503, detail="Service Unavailable")
        
    # Reset for next test
    failure_count = 0
    
    return {"status": "success", "upstream_id": data.get("id", "unknown")}
