from typing import Dict, Any, List, Optional
import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()

class AIService:
    """Mock AI service for demo purposes"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.local_ai_url = os.getenv("LOCAL_AI_URL", "http://localhost:8080")
    
    async def generate_completion(self, prompt: str, model: str = "gpt-3.5-turbo", 
                                provider: str = "openai", max_tokens: int = 2000,
                                temperature: float = 0.7) -> str:
        """Mock text completion - returns a simulated response"""
        
        # For demo purposes, return a mock response based on the prompt
        if "research plan" in prompt.lower():
            return json.dumps({
                "research_questions": [
                    "What are the current trends in this topic?",
                    "What are the key challenges and opportunities?",
                    "What do experts predict for the future?"
                ],
                "keywords": ["trend", "innovation", "technology", "future"],
                "sources": ["academic papers", "industry reports", "expert interviews"],
                "methodology": "Comprehensive analysis of recent developments and expert opinions",
                "deliverables": ["Research summary", "Trend analysis", "Recommendations"]
            })
        elif "tags" in prompt.lower():
            return json.dumps(["technology", "innovation", "trends", "analysis"])
        elif "metadata" in prompt.lower():
            return json.dumps({
                "summary": "Comprehensive analysis of current trends and future opportunities in the technology sector.",
                "category": "Technology",
                "difficulty_level": "intermediate",
                "estimated_read_time": 5,
                "key_concepts": ["innovation", "trends", "technology", "analysis", "future"]
            })
        elif "blog post" in prompt.lower():
            return json.dumps({
                "title": "Understanding Current Technology Trends",
                "content": "# Understanding Current Technology Trends\\n\\nThis post explores the latest developments in technology and their impact on various industries.\\n\\n## Key Trends\\n\\n1. **Artificial Intelligence**: AI continues to revolutionize industries\\n2. **Cloud Computing**: Scalable solutions for modern businesses\\n3. **IoT Integration**: Connected devices creating smart environments\\n\\n## Conclusion\\n\\nThese trends will continue to shape our technological landscape in the coming years.",
                "summary": "An overview of current technology trends and their impact on various industries."
            })
        else:
            return "This is a mock AI response for the given prompt: " + prompt[:100] + "..."
    
    async def generate_research_plan(self, topic: str, agent_role: str = "researcher") -> Dict[str, Any]:
        """Generate a mock research plan for a given topic"""
        return {
            "research_questions": [
                f"What are the key aspects of {topic}?",
                f"What are the current trends in {topic}?",
                f"What challenges and opportunities exist in {topic}?"
            ],
            "keywords": [topic.lower(), "trends", "analysis", "research"],
            "sources": ["academic papers", "industry reports", "news articles", "expert opinions"],
            "methodology": f"Comprehensive analysis of {topic} through multiple sources and perspectives",
            "deliverables": ["Research summary", "Key findings", "Trend analysis", "Recommendations"]
        }
    
    async def generate_tags(self, content: str, max_tags: int = 10) -> List[str]:
        """Generate mock tags for content"""
        # Simple keyword extraction simulation
        words = content.lower().split()
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        unique_words = list(set(word.strip('.,!?;:') for word in words if word not in common_words and len(word) > 3))
        
        # Add some common tech-related tags
        tech_tags = ["technology", "innovation", "analysis", "research", "trends"]
        
        all_tags = unique_words + tech_tags
        return list(set(all_tags))[:max_tags]
    
    async def generate_metadata(self, content: str) -> Dict[str, Any]:
        """Generate mock metadata for content"""
        word_count = len(content.split())
        read_time = max(1, word_count // 200)  # Assume 200 words per minute
        
        return {
            "summary": "Analysis and insights based on research findings.",
            "category": "Research",
            "difficulty_level": "intermediate",
            "estimated_read_time": read_time,
            "key_concepts": ["analysis", "research", "insights", "findings"]
        }
    
    async def generate_blog_post(self, research_data: Dict[str, Any], topic: str) -> Dict[str, str]:
        """Generate a mock blog post from research data"""
        return {
            "title": f"Insights on {topic}: A Comprehensive Analysis",
            "content": f"""# Insights on {topic}: A Comprehensive Analysis

## Introduction

This post presents a comprehensive analysis of {topic} based on recent research and findings.

## Key Findings

Based on our research, here are the most important discoveries:

1. **Trend Analysis**: Current developments show significant growth in this area
2. **Market Insights**: Industry data reveals emerging opportunities
3. **Expert Opinions**: Leading professionals share their perspectives

## Research Methodology

Our analysis employed a multi-faceted approach:
- Literature review of recent publications
- Industry report analysis
- Expert interviews and surveys
- Data trend analysis

## Conclusion

The research reveals that {topic} continues to evolve rapidly, presenting both challenges and opportunities for stakeholders. Organizations should consider these insights when developing their strategies.

## Recommendations

1. Stay informed about emerging trends
2. Invest in relevant technologies and skills
3. Build strategic partnerships
4. Monitor market developments regularly

*This analysis is based on comprehensive research conducted using advanced AI-powered tools.*
""",
            "summary": f"A comprehensive analysis of {topic} based on recent research, revealing key trends, insights, and recommendations for stakeholders."
        }

# Global instance
ai_service = AIService()