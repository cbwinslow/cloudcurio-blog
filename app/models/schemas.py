from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AgentBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    role: str = Field(..., max_length=50)
    config: Optional[Dict[str, Any]] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    role: Optional[str] = Field(None, max_length=50)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class Agent(AgentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CrewBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    agent_ids: List[int] = []
    config: Optional[Dict[str, Any]] = None

class CrewCreate(CrewBase):
    pass

class CrewUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    agent_ids: Optional[List[int]] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class Crew(CrewBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: str
    source_url: Optional[str] = Field(None, max_length=500)
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = []

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResearchRequest(BaseModel):
    topic: str = Field(..., max_length=200)
    query: str
    agent_id: Optional[int] = None
    crew_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class ResearchSession(BaseModel):
    id: int
    topic: str
    query: str
    agent_id: Optional[int] = None
    crew_id: Optional[int] = None
    status: str
    results: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BlogPostBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    summary: Optional[str] = None
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = None

class BlogPostCreate(BlogPostBase):
    research_session_id: Optional[int] = None

class BlogPost(BlogPostBase):
    id: int
    research_session_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True