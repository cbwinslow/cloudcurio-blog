from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routers import agents, research, blog, rag
from app.database.connection import init_db
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="CloudCurio Blog Multi-Agent RAG System",
    description="AI-powered blog system with multi-agent research and RAG capabilities",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(research.router, prefix="/api/research", tags=["Research"])
app.include_router(blog.router, prefix="/api/blog", tags=["Blog"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])

@app.get("/")
async def root():
    return FileResponse('static/index.html')

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )