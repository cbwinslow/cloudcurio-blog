from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database.connection import get_db
from app.agents.service import agent_service, crew_service
from app.models.schemas import Agent, AgentCreate, AgentUpdate, Crew, CrewCreate, CrewUpdate

router = APIRouter()

# Agent endpoints
@router.post("/", response_model=Agent)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new agent"""
    return await agent_service.create_agent(db, agent)

@router.get("/", response_model=List[Agent])
async def list_agents(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all agents"""
    return await agent_service.get_agents(db, skip, limit)

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Get an agent by ID"""
    agent = await agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: int, agent_update: AgentUpdate, db: AsyncSession = Depends(get_db)):
    """Update an agent"""
    agent = await agent_service.update_agent(db, agent_id, agent_update)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an agent"""
    success = await agent_service.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}

# Crew endpoints
@router.post("/crews", response_model=Crew)
async def create_crew(crew: CrewCreate, db: AsyncSession = Depends(get_db)):
    """Create a new crew"""
    try:
        return await crew_service.create_crew(db, crew)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/crews", response_model=List[Crew])
async def list_crews(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all crews"""
    return await crew_service.get_crews(db, skip, limit)

@router.get("/crews/{crew_id}", response_model=Crew)
async def get_crew(crew_id: int, db: AsyncSession = Depends(get_db)):
    """Get a crew by ID"""
    crew = await crew_service.get_crew(db, crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    return crew

@router.put("/crews/{crew_id}", response_model=Crew)
async def update_crew(crew_id: int, crew_update: CrewUpdate, db: AsyncSession = Depends(get_db)):
    """Update a crew"""
    try:
        crew = await crew_service.update_crew(db, crew_id, crew_update)
        if not crew:
            raise HTTPException(status_code=404, detail="Crew not found")
        return crew
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/crews/{crew_id}")
async def delete_crew(crew_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a crew"""
    success = await crew_service.delete_crew(db, crew_id)
    if not success:
        raise HTTPException(status_code=404, detail="Crew not found")
    return {"message": "Crew deleted successfully"}

@router.get("/crews/{crew_id}/agents", response_model=List[Agent])
async def get_crew_agents(crew_id: int, db: AsyncSession = Depends(get_db)):
    """Get all agents in a crew"""
    return await crew_service.get_crew_agents(db, crew_id)