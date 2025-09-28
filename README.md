# CloudCurio Blog - Multi-Agent RAG System

A comprehensive AI-powered blog system with multi-agent research capabilities and RAG (Retrieval-Augmented Generation) integration.

## Features

🤖 **Multi-Agent Environment**
- Configurable AI agents with different roles (researcher, writer, analyst)
- Agent crews for collaborative research tasks
- Persistent agent configurations and state management

🔍 **Advanced RAG System**
- Integration with OpenSearch for vector similarity search
- PostgreSQL with pgvector for scalable document storage
- Automatic document embedding and indexing
- Intelligent document retrieval based on semantic similarity

🧠 **AI Integration**
- Support for OpenAI, OpenRouter, and Local AI providers
- Automatic research planning and execution
- AI-powered content generation and blog post creation
- Smart tagging and metadata generation

📚 **Research Automation**
- Automated research session orchestration
- Web scraping and data collection (configurable)
- Knowledge base building and maintenance
- Research result synthesis and analysis

📝 **Content Management**
- Automated blog post generation from research
- Draft and publication workflow
- Tag-based content organization
- Metadata-rich content structure

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web UI        │    │   FastAPI        │    │   Database      │
│   (React/HTML)  │◄──►│   Backend        │◄──►│   (PostgreSQL)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Multi-Agent    │
                    │   Framework      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐    ┌─────────────────┐
                    │   RAG System     │◄──►│   OpenSearch    │
                    │   (Vector DB)    │    │   (Vector Index)│
                    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   AI Providers   │
                    │ OpenAI/OpenRouter│
                    │   /Local AI      │
                    └──────────────────┘
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL with pgvector extension
- OpenSearch 2.11+
- Redis (optional, for task queue)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd cloudcurio-blog
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application:
- Web UI: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up databases:
```bash
# PostgreSQL setup
createdb cloudcurio_blog
psql cloudcurio_blog -c "CREATE EXTENSION vector;"

# Start OpenSearch
docker run -p 9200:9200 -e "discovery.type=single-node" opensearchproject/opensearch:2.11.0
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/cloudcurio_blog

# OpenSearch Configuration
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_INDEX=blog_documents

# AI Configuration
OPENAI_API_KEY=your_openai_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
LOCAL_AI_URL=http://localhost:8080

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
SECRET_KEY=your_secret_key_here
```

## Usage

### Creating Agents

```python
# Via API
POST /api/agents/
{
    "name": "Research Specialist",
    "role": "researcher",
    "description": "Specialized in conducting comprehensive research on technology topics",
    "config": {
        "max_research_depth": 5,
        "preferred_sources": ["academic", "industry"]
    }
}
```

### Starting Research Sessions

```python
# Via API
POST /api/research/start
{
    "topic": "Artificial Intelligence in Healthcare",
    "query": "What are the latest developments in AI-powered diagnostic tools?",
    "agent_id": 1
}
```

### Managing Knowledge Base

```python
# Add documents to RAG system
POST /api/rag/documents
{
    "title": "AI Healthcare Research Paper",
    "content": "...",
    "source_url": "https://example.com/paper.pdf",
    "tags": ["ai", "healthcare", "diagnostics"]
}

# Search knowledge base
POST /api/rag/search
{
    "query": "AI diagnostic tools",
    "k": 10
}
```

### Generating Blog Posts

```python
# Generate from research session
POST /api/blog/generate-from-research/1
```

## API Documentation

The system provides comprehensive REST APIs:

- **Agent Management**: `/api/agents/*`
- **Research Operations**: `/api/research/*`
- **RAG System**: `/api/rag/*`
- **Blog Management**: `/api/blog/*`

Visit `/docs` when running the server for interactive API documentation.

## Multi-Agent Framework

### Agent Types

1. **Researcher Agents**
   - Web scraping and data collection
   - Academic paper analysis
   - Trend identification

2. **Writer Agents**
   - Content generation
   - Style adaptation
   - SEO optimization

3. **Analyst Agents**
   - Data synthesis
   - Insight extraction
   - Quality assessment

### Crew Configuration

Agents can be organized into crews for collaborative tasks:

```python
{
    "name": "Tech Research Crew",
    "agent_ids": [1, 2, 3],
    "config": {
        "coordination_strategy": "sequential",
        "quality_threshold": 0.8
    }
}
```

## RAG System Details

### Vector Storage
- Documents stored in PostgreSQL with pgvector
- Embeddings generated using sentence-transformers
- Efficient similarity search with configurable distance metrics

### Search Strategy
- Hybrid search combining vector similarity and text matching
- Filtered search by metadata and tags
- Relevance scoring and ranking

### Document Processing
- Automatic text extraction and preprocessing
- Chunking for large documents
- Metadata extraction and enhancement

## AI Provider Integration

### Supported Providers

1. **OpenAI**
   - GPT-3.5/4 for text generation
   - Embedding models for vector search
   - Function calling for structured outputs

2. **OpenRouter**
   - Access to multiple LLM providers
   - Cost optimization
   - Provider fallbacks

3. **Local AI**
   - Self-hosted models
   - Privacy-focused deployment
   - Custom model integration

### Provider Selection Strategy
- Automatic provider selection based on task requirements
- Fallback mechanisms for reliability
- Cost and performance optimization

## Development

### Project Structure
```
app/
├── main.py              # FastAPI application entry point
├── models/              # Database models and schemas
├── database/            # Database connection and utilities
├── agents/              # Multi-agent system
├── rag/                 # RAG system components
├── services/            # Business logic services
├── api/                 # REST API routes
└── utils/               # Utility functions

static/                  # Web UI assets
docker-compose.yml       # Docker orchestration
requirements.txt         # Python dependencies
```

### Adding New Agents

1. Define agent configuration schema
2. Implement agent behavior in `agents/` module
3. Register agent type in the system
4. Add API endpoints if needed

### Extending RAG Capabilities

1. Implement new document processors in `rag/`
2. Add custom embedding models
3. Create specialized search strategies
4. Integrate additional vector databases

## Deployment

### Production Deployment

1. **Container Orchestration**
   - Use Docker Compose or Kubernetes
   - Configure persistent volumes for data
   - Set up load balancing for high availability

2. **Database Setup**
   - Use managed PostgreSQL with pgvector
   - Configure OpenSearch cluster
   - Set up Redis for caching and queues

3. **Security**
   - Configure API authentication
   - Set up HTTPS/TLS
   - Secure database connections
   - Implement rate limiting

4. **Monitoring**
   - Application logs and metrics
   - Database performance monitoring
   - AI provider usage tracking
   - Research session analytics

### Scaling Considerations

- Horizontal scaling of API services
- Database read replicas
- Distributed task processing
- CDN for static assets
- Caching strategies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check the documentation
- Review existing discussions

---

**Note**: This system is designed for educational and research purposes. Ensure compliance with AI provider terms of service and data privacy regulations when deploying in production.
