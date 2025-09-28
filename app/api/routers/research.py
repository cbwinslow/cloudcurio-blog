from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database.connection import get_db
from app.services.research_service import research_service
from app.models.schemas import ResearchRequest, ResearchSession

router = APIRouter()

@router.post("/start", response_model=ResearchSession)
async def start_research(request: ResearchRequest, db: AsyncSession = Depends(get_db)):
    """Start a new research session"""
    try:
        return await research_service.start_research(db, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions", response_model=List[ResearchSession])
async def list_research_sessions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all research sessions"""
    return await research_service.list_research_sessions(db, skip, limit)

@router.get("/sessions/{session_id}", response_model=ResearchSession)
async def get_research_session(session_id: int, db: AsyncSession = Depends(get_db)):
    """Get a research session by ID"""
    session = await research_service.get_research_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found")
    return session