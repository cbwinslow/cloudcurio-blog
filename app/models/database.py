from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    role = Column(String(50))  # researcher, writer, analyst, etc.
    config = Column(JSON)  # Agent configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Crew(Base):
    __tablename__ = "crews"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    agent_ids = Column(JSON)  # List of agent IDs
    config = Column(JSON)  # Crew configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    source_url = Column(String(500))
    metadata = Column(JSON)
    tags = Column(JSON)  # List of tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ResearchSession(Base):
    __tablename__ = "research_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(200))
    query = Column(Text)
    agent_id = Column(Integer)
    crew_id = Column(Integer)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    results = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    summary = Column(Text)
    tags = Column(JSON)
    metadata = Column(JSON)
    research_session_id = Column(Integer)
    status = Column(String(20), default="draft")  # draft, published, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))