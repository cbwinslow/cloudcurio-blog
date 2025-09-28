from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from app.database.connection import get_db
from app.models.database import BlogPost as BlogPostModel, ResearchSession as ResearchSessionModel
from app.models.schemas import BlogPost, BlogPostCreate
from app.services.ai_service import ai_service
import json

router = APIRouter()

@router.post("/", response_model=BlogPost)
async def create_blog_post(post: BlogPostCreate, db: AsyncSession = Depends(get_db)):
    """Create a new blog post"""
    try:
        db_post = BlogPostModel(
            title=post.title,
            content=post.content,
            summary=post.summary,
            tags=post.tags or [],
            metadata=post.metadata or {},
            research_session_id=post.research_session_id
        )
        
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        
        return BlogPost.from_orm(db_post)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[BlogPost])
async def list_blog_posts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    db: AsyncSession = Depends(get_db)
):
    """List all blog posts with optional filters"""
    query = select(BlogPostModel).offset(skip).limit(limit).order_by(BlogPostModel.created_at.desc())
    
    if status:
        query = query.where(BlogPostModel.status == status)
    
    # Note: Tag filtering would require more complex SQL for JSON arrays
    # This is a simplified version
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    return [BlogPost.from_orm(post) for post in posts]

@router.get("/{post_id}", response_model=BlogPost)
async def get_blog_post(post_id: int, db: AsyncSession = Depends(get_db)):
    """Get a blog post by ID"""
    result = await db.execute(select(BlogPostModel).where(BlogPostModel.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return BlogPost.from_orm(post)

@router.put("/{post_id}", response_model=BlogPost)
async def update_blog_post(post_id: int, updates: dict, db: AsyncSession = Depends(get_db)):
    """Update a blog post"""
    result = await db.execute(select(BlogPostModel).where(BlogPostModel.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    for field, value in updates.items():
        if hasattr(post, field):
            setattr(post, field, value)
    
    await db.commit()
    await db.refresh(post)
    
    return BlogPost.from_orm(post)

@router.delete("/{post_id}")
async def delete_blog_post(post_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a blog post"""
    result = await db.execute(select(BlogPostModel).where(BlogPostModel.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    await db.delete(post)
    await db.commit()
    
    return {"message": "Blog post deleted successfully"}

@router.post("/generate-from-research/{research_session_id}", response_model=BlogPost)
async def generate_blog_post_from_research(research_session_id: int, db: AsyncSession = Depends(get_db)):
    """Generate a blog post from a research session"""
    try:
        # Get the research session
        result = await db.execute(
            select(ResearchSessionModel).where(ResearchSessionModel.id == research_session_id)
        )
        research_session = result.scalar_one_or_none()
        
        if not research_session:
            raise HTTPException(status_code=404, detail="Research session not found")
        
        if research_session.status != "completed":
            raise HTTPException(status_code=400, detail="Research session not completed")
        
        # Generate blog post from research data
        blog_data = await ai_service.generate_blog_post(
            research_session.results,
            research_session.topic
        )
        
        # Create the blog post
        db_post = BlogPostModel(
            title=blog_data.get("title", f"Blog Post: {research_session.topic}"),
            content=blog_data.get("content", ""),
            summary=blog_data.get("summary", ""),
            tags=research_session.results.get("tags", []),
            metadata={
                "generated_from_research": True,
                "research_session_id": research_session_id,
                **research_session.results.get("metadata", {})
            },
            research_session_id=research_session_id,
            status="draft"
        )
        
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        
        return BlogPost.from_orm(db_post)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{post_id}/publish")
async def publish_blog_post(post_id: int, db: AsyncSession = Depends(get_db)):
    """Publish a blog post"""
    result = await db.execute(select(BlogPostModel).where(BlogPostModel.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    post.status = "published"
    from datetime import datetime
    post.published_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(post)
    
    return BlogPost.from_orm(post)