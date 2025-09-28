from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from app.database.connection import get_db
from app.rag.service import rag_service
from app.models.schemas import Document, DocumentCreate

router = APIRouter()

@router.post("/documents", response_model=Document)
async def add_document(document: DocumentCreate, db: AsyncSession = Depends(get_db)):
    """Add a document to the RAG system"""
    try:
        return await rag_service.add_document(db, document)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Get a document by ID"""
    document = await rag_service.get_document(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.put("/documents/{document_id}", response_model=Document)
async def update_document(document_id: int, updates: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """Update a document"""
    try:
        document = await rag_service.update_document(db, document_id, updates)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a document"""
    success = await rag_service.delete_document(db, document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

@router.post("/search")
async def search_documents(
    query: str,
    k: int = Query(10, description="Number of documents to return"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    db: AsyncSession = Depends(get_db)
):
    """Search documents using RAG"""
    try:
        filters = {}
        if tags:
            filters["tags"] = tags
        
        results = await rag_service.search_documents(query, k, filters)
        return {
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-context")
async def generate_context(query: str, max_tokens: int = Query(4000), db: AsyncSession = Depends(get_db)):
    """Generate context from RAG search for AI completion"""
    try:
        # Search for relevant documents
        documents = await rag_service.search_documents(query, k=10)
        
        # Generate context
        context = rag_service.generate_context(documents, max_tokens)
        
        return {
            "query": query,
            "context": context,
            "source_documents": len(documents),
            "context_length": len(context)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))