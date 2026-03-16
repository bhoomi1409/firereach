from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator_v2 import run_outreach, OutreachResult
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FireReach API v2",
    description="Autonomous Outreach Engine — Hunter.io powered",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OutreachRequest(BaseModel):
    company_name: str

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0"}

@app.post("/api/outreach", response_model=OutreachResult)
async def run_outreach_endpoint(request: OutreachRequest):
    """
    Single input: company_name
    Output: Complete outreach result with Hunter.io data
    """
    if not request.company_name.strip():
        raise HTTPException(status_code=400, detail="company_name cannot be empty")
    
    result = await run_outreach(request.company_name.strip())
    return result