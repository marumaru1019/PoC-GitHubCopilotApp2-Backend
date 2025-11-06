from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, tickets, articles, admin

app = FastAPI(
    title="Helpdesk & Knowledge Base API",
    description="統合ヘルプデスク＆ナレッジベースシステム",
    version="1.0.0",
)

# CORS設定（開発環境用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(articles.router)
app.include_router(admin.router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Helpdesk & Knowledge Base API", "status": "running"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
