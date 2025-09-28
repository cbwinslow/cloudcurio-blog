from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import Agent as AgentModel, Crew as CrewModel
from app.models.schemas import Agent, AgentCreate, AgentUpdate, Crew, CrewCreate, CrewUpdate
from app.services.ai_service import ai_service
import json

class AgentService:
    """Service for managing individual agents"""
    
    async def create_agent(self, db: AsyncSession, agent_data: AgentCreate) -> Agent:
        """Create a new agent"""
        db_agent = AgentModel(
            name=agent_data.name,
            description=agent_data.description,
            role=agent_data.role,
            config=agent_data.config or {}
        )
        
        db.add(db_agent)
        await db.commit()
        await db.refresh(db_agent)
        
        return Agent.from_orm(db_agent)
    
    async def get_agent(self, db: AsyncSession, agent_id: int) -> Optional[Agent]:
        """Get an agent by ID"""
        result = await db.execute(select(AgentModel).where(AgentModel.id == agent_id))
        db_agent = result.scalar_one_or_none()
        
        if db_agent:
            return Agent.from_orm(db_agent)
        return None
    
    async def get_agents(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get all agents with pagination"""
        result = await db.execute(
            select(AgentModel).offset(skip).limit(limit).where(AgentModel.is_active == True)
        )
        agents = result.scalars().all()
        
        return [Agent.from_orm(agent) for agent in agents]
    
    async def update_agent(self, db: AsyncSession, agent_id: int, 
                          agent_update: AgentUpdate) -> Optional[Agent]:
        """Update an agent"""
        result = await db.execute(select(AgentModel).where(AgentModel.id == agent_id))
        db_agent = result.scalar_one_or_none()
        
        if not db_agent:
            return None
        
        update_data = agent_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_agent, field, value)
        
        await db.commit()
        await db.refresh(db_agent)
        
        return Agent.from_orm(db_agent)
    
    async def delete_agent(self, db: AsyncSession, agent_id: int) -> bool:
        """Soft delete an agent"""
        result = await db.execute(select(AgentModel).where(AgentModel.id == agent_id))
        db_agent = result.scalar_one_or_none()
        
        if not db_agent:
            return False
        
        db_agent.is_active = False
        await db.commit()
        
        return True

class CrewService:
    """Service for managing agent crews"""
    
    def __init__(self):
        self.agent_service = AgentService()
    
    async def create_crew(self, db: AsyncSession, crew_data: CrewCreate) -> Crew:
        """Create a new crew"""
        # Validate that all agent IDs exist
        for agent_id in crew_data.agent_ids:
            agent = await self.agent_service.get_agent(db, agent_id)
            if not agent:
                raise ValueError(f"Agent with ID {agent_id} not found")
        
        db_crew = CrewModel(
            name=crew_data.name,
            description=crew_data.description,
            agent_ids=crew_data.agent_ids,
            config=crew_data.config or {}
        )
        
        db.add(db_crew)
        await db.commit()
        await db.refresh(db_crew)
        
        return Crew.from_orm(db_crew)
    
    async def get_crew(self, db: AsyncSession, crew_id: int) -> Optional[Crew]:
        """Get a crew by ID"""
        result = await db.execute(select(CrewModel).where(CrewModel.id == crew_id))
        db_crew = result.scalar_one_or_none()
        
        if db_crew:
            return Crew.from_orm(db_crew)
        return None
    
    async def get_crews(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Crew]:
        """Get all crews with pagination"""
        result = await db.execute(
            select(CrewModel).offset(skip).limit(limit).where(CrewModel.is_active == True)
        )
        crews = result.scalars().all()
        
        return [Crew.from_orm(crew) for crew in crews]
    
    async def update_crew(self, db: AsyncSession, crew_id: int, 
                         crew_update: CrewUpdate) -> Optional[Crew]:
        """Update a crew"""
        result = await db.execute(select(CrewModel).where(CrewModel.id == crew_id))
        db_crew = result.scalar_one_or_none()
        
        if not db_crew:
            return None
        
        update_data = crew_update.dict(exclude_unset=True)
        
        # Validate agent IDs if they're being updated
        if "agent_ids" in update_data:
            for agent_id in update_data["agent_ids"]:
                agent = await self.agent_service.get_agent(db, agent_id)
                if not agent:
                    raise ValueError(f"Agent with ID {agent_id} not found")
        
        for field, value in update_data.items():
            setattr(db_crew, field, value)
        
        await db.commit()
        await db.refresh(db_crew)
        
        return Crew.from_orm(db_crew)
    
    async def delete_crew(self, db: AsyncSession, crew_id: int) -> bool:
        """Soft delete a crew"""
        result = await db.execute(select(CrewModel).where(CrewModel.id == crew_id))
        db_crew = result.scalar_one_or_none()
        
        if not db_crew:
            return False
        
        db_crew.is_active = False
        await db.commit()
        
        return True
    
    async def get_crew_agents(self, db: AsyncSession, crew_id: int) -> List[Agent]:
        """Get all agents in a crew"""
        crew = await self.get_crew(db, crew_id)
        if not crew:
            return []
        
        agents = []
        for agent_id in crew.agent_ids:
            agent = await self.agent_service.get_agent(db, agent_id)
            if agent:
                agents.append(agent)
        
        return agents

# Global instances
agent_service = AgentService()
crew_service = CrewService()