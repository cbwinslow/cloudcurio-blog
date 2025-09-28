from typing import List, Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

class OpenSearchService:
    """Mock OpenSearch service for demo purposes"""
    
    def __init__(self):
        self.documents = {}  # In-memory storage for demo
        self.next_id = 1
    
    def create_index(self):
        """Mock index creation"""
        pass
    
    def add_document(self, doc_id: str, title: str, content: str, 
                     source_url: Optional[str] = None, tags: List[str] = None, 
                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a document to the mock index"""
        
        document = {
            "title": title,
            "content": content,
            "source_url": source_url,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": "now"
        }
        
        self.documents[doc_id] = document
        
        return {"_id": doc_id, "result": "created"}
    
    def search_documents(self, query: str, k: int = 10, 
                        filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Mock document search using simple text matching"""
        
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in self.documents.items():
            score = 0.0
            
            # Simple scoring based on term occurrence
            title = doc.get("title", "").lower()
            content = doc.get("content", "").lower()
            
            if query_lower in title:
                score += 2.0
            if query_lower in content:
                score += 1.0
            
            if score > 0:
                result = {
                    "id": doc_id,
                    "score": score,
                    **doc
                }
                results.append(result)
        
        # Sort by score and return top k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        doc = self.documents.get(doc_id)
        if doc:
            return {"id": doc_id, **doc}
        return None
    
    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document by ID"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            return {"_id": doc_id, "result": "deleted"}
        return {"_id": doc_id, "result": "not_found"}
    
    def update_document(self, doc_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document"""
        if doc_id in self.documents:
            self.documents[doc_id].update(updates)
            return {"_id": doc_id, "result": "updated"}
        return {"_id": doc_id, "result": "not_found"}

# Global instance
opensearch_service = OpenSearchService()