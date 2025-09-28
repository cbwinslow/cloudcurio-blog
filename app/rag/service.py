from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import Document as DocumentModel
from app.models.schemas import Document, DocumentCreate
from app.rag.opensearch import opensearch_service
from app.database.connection import get_db
import uuid

class RAGService:
    def __init__(self):
        self.opensearch = opensearch_service
    
    async def add_document(self, db: AsyncSession, document_data: DocumentCreate) -> Document:
        """Add a document to both PostgreSQL and OpenSearch"""
        
        # Create document in PostgreSQL
        db_document = DocumentModel(
            title=document_data.title,
            content=document_data.content,
            source_url=document_data.source_url,
            metadata=document_data.metadata,
            tags=document_data.tags,
        )
        
        db.add(db_document)
        await db.commit()
        await db.refresh(db_document)
        
        # Add to OpenSearch
        doc_id = str(db_document.id)
        self.opensearch.add_document(
            doc_id=doc_id,
            title=document_data.title or "",
            content=document_data.content,
            source_url=document_data.source_url,
            tags=document_data.tags or [],
            metadata=document_data.metadata or {}
        )
        
        return Document.from_orm(db_document)
    
    async def search_documents(self, query: str, k: int = 10, 
                             filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search documents using OpenSearch"""
        return self.opensearch.search_documents(query, k, filters)
    
    async def get_document(self, db: AsyncSession, document_id: int) -> Optional[Document]:
        """Get a document by ID from PostgreSQL"""
        result = await db.execute(select(DocumentModel).where(DocumentModel.id == document_id))
        db_document = result.scalar_one_or_none()
        
        if db_document:
            return Document.from_orm(db_document)
        return None
    
    async def update_document(self, db: AsyncSession, document_id: int, 
                            updates: Dict[str, Any]) -> Optional[Document]:
        """Update a document in both PostgreSQL and OpenSearch"""
        
        result = await db.execute(select(DocumentModel).where(DocumentModel.id == document_id))
        db_document = result.scalar_one_or_none()
        
        if not db_document:
            return None
        
        # Update PostgreSQL
        for field, value in updates.items():
            if hasattr(db_document, field):
                setattr(db_document, field, value)
        
        await db.commit()
        await db.refresh(db_document)
        
        # Update OpenSearch
        doc_id = str(document_id)
        opensearch_updates = {
            k: v for k, v in updates.items() 
            if k in ['title', 'content', 'source_url', 'tags', 'metadata']
        }
        
        if opensearch_updates:
            self.opensearch.update_document(doc_id, opensearch_updates)
        
        return Document.from_orm(db_document)
    
    async def delete_document(self, db: AsyncSession, document_id: int) -> bool:
        """Delete a document from both PostgreSQL and OpenSearch"""
        
        result = await db.execute(select(DocumentModel).where(DocumentModel.id == document_id))
        db_document = result.scalar_one_or_none()
        
        if not db_document:
            return False
        
        # Delete from PostgreSQL
        await db.delete(db_document)
        await db.commit()
        
        # Delete from OpenSearch
        doc_id = str(document_id)
        try:
            self.opensearch.delete_document(doc_id)
        except Exception:
            pass  # Document might not exist in OpenSearch
        
        return True
    
    def generate_context(self, documents: List[Dict[str, Any]], max_tokens: int = 4000) -> str:
        """Generate context from retrieved documents for RAG"""
        context_parts = []
        current_length = 0
        
        for doc in documents:
            doc_text = f"Title: {doc.get('title', '')}\n"
            doc_text += f"Content: {doc.get('content', '')}\n"
            doc_text += f"Source: {doc.get('source_url', 'N/A')}\n"
            doc_text += "---\n"
            
            # Estimate token count (rough approximation: 1 token ≈ 4 characters)
            estimated_tokens = len(doc_text) // 4
            
            if current_length + estimated_tokens > max_tokens:
                break
            
            context_parts.append(doc_text)
            current_length += estimated_tokens
        
        return "\n".join(context_parts)

# Global instance
rag_service = RAGService()