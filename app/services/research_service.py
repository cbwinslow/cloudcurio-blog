from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.database import ResearchSession as ResearchSessionModel, Document as DocumentModel
from app.models.schemas import ResearchRequest, ResearchSession
from app.services.ai_service import ai_service
from app.rag.service import rag_service
from app.agents.service import agent_service, crew_service
import httpx
import json
import uuid
from datetime import datetime

class ResearchService:
    """Service for orchestrating multi-agent research"""
    
    def __init__(self):
        self.ai_service = ai_service
        self.rag_service = rag_service
        self.agent_service = agent_service
        self.crew_service = crew_service
    
    async def start_research(self, db: AsyncSession, request: ResearchRequest) -> ResearchSession:
        """Start a new research session"""
        
        # Create research session
        db_session = ResearchSessionModel(
            topic=request.topic,
            query=request.query,
            agent_id=request.agent_id,
            crew_id=request.crew_id,
            status="pending",
            metadata=request.metadata or {}
        )
        
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        
        # Start research process asynchronously
        research_session = ResearchSession.from_orm(db_session)
        
        # For now, we'll process synchronously, but this could be moved to a background task
        await self._conduct_research(db, db_session.id)
        
        # Refresh to get updated status
        await db.refresh(db_session)
        return ResearchSession.from_orm(db_session)
    
    async def _conduct_research(self, db: AsyncSession, session_id: int):
        """Conduct the actual research process"""
        
        try:
            # Update status to running
            await db.execute(
                update(ResearchSessionModel)
                .where(ResearchSessionModel.id == session_id)
                .values(status="running")
            )
            await db.commit()
            
            # Get the research session
            result = await db.execute(
                select(ResearchSessionModel).where(ResearchSessionModel.id == session_id)
            )
            session = result.scalar_one()
            
            # Step 1: Generate research plan
            research_plan = await self.ai_service.generate_research_plan(
                session.topic, 
                agent_role="researcher"
            )
            
            # Step 2: Search existing knowledge base
            existing_docs = await self.rag_service.search_documents(
                session.query, k=10
            )
            
            # Step 3: Conduct web research (simulate for now)
            web_research_results = await self._simulate_web_research(
                session.topic, research_plan.get("keywords", [])
            )
            
            # Step 4: Analyze and synthesize results
            analysis = await self._analyze_research_results(
                session.topic, existing_docs, web_research_results
            )
            
            # Step 5: Generate tags and metadata
            content_for_analysis = f"{session.topic} {session.query} {json.dumps(analysis)}"
            tags = await self.ai_service.generate_tags(content_for_analysis)
            metadata = await self.ai_service.generate_metadata(content_for_analysis)
            
            # Step 6: Store results
            results = {
                "research_plan": research_plan,
                "existing_knowledge": existing_docs,
                "web_research": web_research_results,
                "analysis": analysis,
                "tags": tags,
                "metadata": metadata,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            # Step 7: Store research as documents in the knowledge base
            await self._store_research_documents(db, session_id, results)
            
            # Update session with results
            await db.execute(
                update(ResearchSessionModel)
                .where(ResearchSessionModel.id == session_id)
                .values(
                    status="completed",
                    results=results,
                    metadata={**session.metadata, **metadata}
                )
            )
            await db.commit()
            
        except Exception as e:
            # Update status to failed
            await db.execute(
                update(ResearchSessionModel)
                .where(ResearchSessionModel.id == session_id)
                .values(
                    status="failed",
                    results={"error": str(e), "failed_at": datetime.utcnow().isoformat()}
                )
            )
            await db.commit()
            raise
    
    async def _simulate_web_research(self, topic: str, keywords: List[str]) -> Dict[str, Any]:
        """Simulate web research (in a real implementation, this would use web scraping/APIs)"""
        
        # This is a simulation - in a real implementation, you would:
        # 1. Use search APIs (Google, Bing, etc.)
        # 2. Scrape relevant websites
        # 3. Use RSS feeds
        # 4. Query academic databases
        # 5. Use social media APIs
        
        prompt = f"""
        Simulate comprehensive web research results for the topic: "{topic}"
        Keywords: {', '.join(keywords)}
        
        Provide realistic research findings including:
        1. Key statistics or data points
        2. Recent developments or news
        3. Expert opinions or quotes
        4. Relevant case studies
        5. Industry trends
        
        Format as JSON with sources, findings, and credibility scores.
        """
        
        try:
            response = await self.ai_service.generate_completion(prompt, temperature=0.5)
            return json.loads(response)
        except:
            # Fallback simulation
            return {
                "sources": [
                    {"url": "https://example.com/research1", "title": f"Research on {topic}", "credibility": 0.8},
                    {"url": "https://example.com/research2", "title": f"Analysis of {topic}", "credibility": 0.9}
                ],
                "findings": [
                    f"Key insight about {topic} from recent studies",
                    f"Important trend related to {topic}",
                    f"Expert opinion on {topic} implications"
                ],
                "statistics": {
                    "market_size": "Growing trend",
                    "adoption_rate": "Increasing",
                    "user_satisfaction": "High"
                }
            }
    
    async def _analyze_research_results(self, topic: str, existing_docs: List[Dict], 
                                      web_research: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and synthesize research results"""
        
        existing_content = ""
        for doc in existing_docs[:5]:  # Limit to top 5 for analysis
            existing_content += f"Title: {doc.get('title', '')}\n"
            existing_content += f"Content: {doc.get('content', '')[:500]}...\n\n"
        
        web_content = json.dumps(web_research, indent=2)
        
        prompt = f"""
        Analyze the following research data for the topic "{topic}" and provide a comprehensive synthesis:
        
        EXISTING KNOWLEDGE:
        {existing_content}
        
        NEW RESEARCH:
        {web_content}
        
        Provide your analysis in JSON format with:
        1. key_findings: List of the most important discoveries
        2. knowledge_gaps: Areas that need more research
        3. contradictions: Any conflicting information found
        4. confidence_score: Overall confidence in the findings (0-1)
        5. recommendations: Suggested next steps or actions
        6. synthesis: A comprehensive summary combining all sources
        
        Be objective and highlight both strengths and limitations of the research.
        """
        
        try:
            response = await self.ai_service.generate_completion(prompt, max_tokens=2000)
            return json.loads(response)
        except:
            # Fallback analysis
            return {
                "key_findings": [f"Important insights about {topic}"],
                "knowledge_gaps": ["Areas requiring further research"],
                "contradictions": [],
                "confidence_score": 0.7,
                "recommendations": ["Continue monitoring developments", "Gather more data"],
                "synthesis": f"Comprehensive analysis of {topic} shows promising trends and opportunities for further exploration."
            }
    
    async def _store_research_documents(self, db: AsyncSession, session_id: int, 
                                      results: Dict[str, Any]):
        """Store research results as documents in the knowledge base"""
        
        # Create a summary document
        summary_content = f"""
        Research Summary: {results.get('research_plan', {}).get('research_questions', [])}
        
        Key Findings:
        {json.dumps(results.get('analysis', {}).get('key_findings', []), indent=2)}
        
        Analysis:
        {results.get('analysis', {}).get('synthesis', '')}
        
        Web Research Results:
        {json.dumps(results.get('web_research', {}), indent=2)}
        """
        
        # Store the research document
        from app.models.schemas import DocumentCreate
        
        doc_data = DocumentCreate(
            title=f"Research: {results.get('research_plan', {}).get('methodology', 'Unknown Topic')}",
            content=summary_content,
            source_url=f"research_session_{session_id}",
            tags=results.get('tags', []),
            metadata={
                "research_session_id": session_id,
                "document_type": "research_summary",
                **results.get('metadata', {})
            }
        )
        
        await self.rag_service.add_document(db, doc_data)
    
    async def get_research_session(self, db: AsyncSession, session_id: int) -> Optional[ResearchSession]:
        """Get a research session by ID"""
        result = await db.execute(
            select(ResearchSessionModel).where(ResearchSessionModel.id == session_id)
        )
        db_session = result.scalar_one_or_none()
        
        if db_session:
            return ResearchSession.from_orm(db_session)
        return None
    
    async def list_research_sessions(self, db: AsyncSession, skip: int = 0, 
                                   limit: int = 100) -> List[ResearchSession]:
        """List research sessions with pagination"""
        result = await db.execute(
            select(ResearchSessionModel)
            .order_by(ResearchSessionModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        sessions = result.scalars().all()
        
        return [ResearchSession.from_orm(session) for session in sessions]

# Global instance
research_service = ResearchService()