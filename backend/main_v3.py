"""
FireReach API v3 — Fully Autonomous
Input: ICP description (3 fields)
Output: Full batch outreach result — companies discovered, scored, emailed
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from orchestrator_v3 import run_autonomous_outreach, BatchOutreachResult

app = FastAPI(title="FireReach", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class ICPRequest(BaseModel):
    what_we_do:       str   # "We sell AI-powered outreach automation..."
    what_they_do:     str   # "Series B SaaS companies with a sales team..."
    why_they_need_us: str   # "Low reply rates, raised funding..."
    max_companies:    Optional[int] = 5   # how many to contact (default 5, max 20)

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0"}

@app.post("/api/outreach", response_model=BatchOutreachResult)
async def outreach(req: ICPRequest):
    # Validate inputs
    if not req.what_we_do.strip():
        raise HTTPException(400, "what_we_do cannot be empty")
    if not req.what_they_do.strip():
        raise HTTPException(400, "what_they_do cannot be empty")
    if not req.why_they_need_us.strip():
        raise HTTPException(400, "why_they_need_us cannot be empty")
    max_co = min(max(1, req.max_companies or 5), 20)  # clamp 1-20

    return await run_autonomous_outreach(
        what_we_do       = req.what_we_do.strip(),
        what_they_do     = req.what_they_do.strip(),
        why_they_need_us = req.why_they_need_us.strip(),
        max_companies    = max_co
    )

# uvicorn main_v3:app --reload