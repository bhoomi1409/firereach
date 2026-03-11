from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import OutreachRequest, OutreachResponse
from agent.orchestrator import run_firereach_agent
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="FireReach API",
    description="Autonomous Outreach Engine — Signal → Research → Send",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FireReach"}

@app.post("/api/outreach", response_model=OutreachResponse)
async def run_outreach(request: OutreachRequest):
    """
    Main endpoint — triggers the 3-tool agentic pipeline.
    Input: ICP + target company + recipient email
    Output: Signals + Account Brief + Email content + Send status
    """
    if not request.icp.strip():
        raise HTTPException(status_code=400, detail="ICP cannot be empty")
    if not request.target_company.strip():
        raise HTTPException(status_code=400, detail="Target company cannot be empty")
    
    result = await run_firereach_agent(
        icp=request.icp,
        target_company=request.target_company,
        recipient_email=str(request.recipient_email),
        sender_name=request.sender_name
    )
    return result