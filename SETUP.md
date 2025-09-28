# CloudCurio Blog Setup Guide

## Quick Start (Demo Mode)

The system can run in demo mode with minimal dependencies for testing and development.

### 1. Install Dependencies

Since the full ML dependencies may have installation issues, you can start with the core system:

```bash
# Install core dependencies
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 sqlalchemy==2.0.23 aiosqlite==0.19.0 pydantic==2.5.0 python-multipart==0.0.6 aiofiles==23.2.0 httpx==0.25.2 python-dotenv==1.0.0

# Optional: Add ML dependencies later
pip install sentence-transformers opensearch-py pgvector psycopg2-binary
```

### 2. Environment Setup

Create a `.env` file:
```bash
cp .env.example .env
```

For demo mode, the system will use SQLite and mock AI services.

### 3. Start the Application

```bash
# Development mode
uvicorn app.main:app --reload

# Or run directly
python -m app.main
```

### 4. Access the System

- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Full Production Setup

### 1. Database Setup

#### PostgreSQL with pgvector
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb cloudcurio_blog

# Install pgvector extension
sudo -u postgres psql cloudcurio_blog -c "CREATE EXTENSION vector;"
```

#### OpenSearch
```bash
# Run with Docker
docker run -d \
  --name opensearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:2.11.0
```

### 2. AI Provider Configuration

#### OpenAI
1. Get API key from https://platform.openai.com/
2. Add to `.env`: `OPENAI_API_KEY=your_key_here`

#### OpenRouter
1. Get API key from https://openrouter.ai/
2. Add to `.env`: `OPENROUTER_API_KEY=your_key_here`

#### Local AI
1. Install LocalAI or similar
2. Configure endpoint in `.env`: `LOCAL_AI_URL=http://localhost:8080`

### 3. Deploy with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration Examples

### Agent Configuration
```json
{
  "name": "Research Specialist",
  "role": "researcher",
  "description": "Conducts comprehensive research on technology topics",
  "config": {
    "max_sources": 20,
    "research_depth": "deep",
    "preferred_domains": ["academic", "industry", "news"],
    "languages": ["en"],
    "quality_threshold": 0.8
  }
}
```

### Crew Configuration
```json
{
  "name": "Content Creation Crew",
  "description": "End-to-end content creation from research to publication",
  "agent_ids": [1, 2, 3],
  "config": {
    "workflow": "sequential",
    "quality_gates": true,
    "parallel_research": false,
    "review_required": true
  }
}
```

### Research Session Example
```json
{
  "topic": "Edge AI and IoT Integration",
  "query": "Analyze the current state and future trends of AI processing at the edge, particularly in IoT environments. Focus on hardware solutions, software frameworks, and real-world applications.",
  "metadata": {
    "priority": "high",
    "deadline": "2024-01-15",
    "target_audience": "technical professionals"
  }
}
```

## API Usage Examples

### Creating and Managing Agents

```python
import requests

# Create an agent
agent_data = {
    "name": "Tech Research Agent",
    "role": "researcher",
    "description": "Specializes in technology research and analysis"
}

response = requests.post("http://localhost:8000/api/agents/", json=agent_data)
agent = response.json()

# List all agents
response = requests.get("http://localhost:8000/api/agents/")
agents = response.json()

# Update an agent
update_data = {"description": "Updated description"}
response = requests.put(f"http://localhost:8000/api/agents/{agent['id']}", json=update_data)
```

### Research Operations

```python
# Start research session
research_request = {
    "topic": "Quantum Computing Applications",
    "query": "What are the practical applications of quantum computing in various industries?",
    "agent_id": 1
}

response = requests.post("http://localhost:8000/api/research/start", json=research_request)
session = response.json()

# Check research status
response = requests.get(f"http://localhost:8000/api/research/sessions/{session['id']}")
session_status = response.json()

# Generate blog post from research
response = requests.post(f"http://localhost:8000/api/blog/generate-from-research/{session['id']}")
blog_post = response.json()
```

### RAG Operations

```python
# Add document to knowledge base
document = {
    "title": "Quantum Computing Overview",
    "content": "Quantum computing represents a paradigm shift...",
    "tags": ["quantum", "computing", "technology"],
    "metadata": {"source": "research", "author": "AI Agent"}
}

response = requests.post("http://localhost:8000/api/rag/documents", json=document)

# Search knowledge base
search_request = {
    "query": "quantum computing applications",
    "k": 5
}

response = requests.post("http://localhost:8000/api/rag/search", json=search_request)
results = response.json()
```

## Monitoring and Maintenance

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/api/agents/?limit=1

# OpenSearch status
curl http://localhost:9200/_cluster/health
```

### Logs and Debugging
```bash
# Application logs
docker-compose logs app

# Database logs
docker-compose logs postgres

# OpenSearch logs
docker-compose logs opensearch
```

### Performance Optimization

1. **Database Indexing**
   - Add indexes on frequently queried columns
   - Monitor query performance
   - Consider partitioning for large datasets

2. **Vector Search Optimization**
   - Tune OpenSearch settings
   - Optimize embedding dimensions
   - Use appropriate similarity metrics

3. **Caching**
   - Implement Redis caching for frequent queries
   - Cache AI API responses
   - Use CDN for static assets

4. **Rate Limiting**
   - Implement API rate limiting
   - Manage AI provider quotas
   - Queue long-running tasks

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify PYTHONPATH settings

2. **Database Connection Issues**
   - Check connection strings
   - Verify database permissions
   - Ensure pgvector extension is installed

3. **AI Provider Errors**
   - Verify API keys
   - Check provider status
   - Monitor usage quotas

4. **Performance Issues**
   - Monitor resource usage
   - Check database query performance
   - Optimize vector search parameters

### Debug Mode

Enable debug mode for detailed logging:
```bash
export DEBUG=true
uvicorn app.main:app --reload --log-level debug
```

## Security Considerations

### API Security
- Implement authentication and authorization
- Use HTTPS in production
- Validate all input data
- Implement rate limiting

### Data Protection
- Encrypt sensitive data at rest
- Secure database connections
- Implement data retention policies
- Anonymize personal information

### AI Provider Security
- Secure API key storage
- Monitor API usage
- Implement content filtering
- Review generated content

## Next Steps

1. **Extend Agent Capabilities**
   - Add specialized agents for different domains
   - Implement agent learning and adaptation
   - Create agent collaboration patterns

2. **Enhance RAG System**
   - Add support for more document types
   - Implement advanced retrieval strategies
   - Create semantic caching

3. **Improve Content Generation**
   - Add content templates
   - Implement style guides
   - Create content workflows

4. **Scale the System**
   - Implement distributed processing
   - Add load balancing
   - Create monitoring dashboards