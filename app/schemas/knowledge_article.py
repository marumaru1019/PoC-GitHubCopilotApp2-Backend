from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.ticket import TagResponse, CategoryResponse, UserBasicResponse


class KnowledgeArticleBase(BaseModel):
    title: str
    content: str
    category_id: Optional[str] = None


class KnowledgeArticleCreate(KnowledgeArticleBase):
    tags: Optional[List[str]] = []


class KnowledgeArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None


class KnowledgeArticleResponse(KnowledgeArticleBase):
    id: str
    status: str  # DRAFT, PUBLISHED, ARCHIVED
    author_id: str
    author: UserBasicResponse
    category: Optional[CategoryResponse] = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


class PaginatedArticleResponse(BaseModel):
    items: List[KnowledgeArticleResponse]
    total: int
    skip: int
    limit: int
