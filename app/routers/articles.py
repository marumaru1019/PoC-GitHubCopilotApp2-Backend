from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_current_operator
from app.db.base import get_db
from app.models.user import User
from app.schemas.knowledge_article import (
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    KnowledgeArticleResponse,
    PaginatedArticleResponse,
)
from app.services import article_service

router = APIRouter(prefix="/api/articles", tags=["knowledge-base"])


@router.post("", response_model=KnowledgeArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    article_data: KnowledgeArticleCreate,
    current_user: User = Depends(get_current_operator),
    db: Session = Depends(get_db),
):
    """Create a new knowledge article (operator/admin only)."""
    article = article_service.create_article(
        db=db,
        title=article_data.title,
        content=article_data.content,
        author_id=current_user.id,
        category_id=article_data.category_id,
        tag_names=article_data.tags,
    )
    return article


@router.get("", response_model=PaginatedArticleResponse)
def list_articles(
    status: Optional[str] = Query(None),
    author_id: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get list of articles with filters."""
    # Requesters can only see published articles
    if current_user.role == "requester":
        status = "PUBLISHED"
    
    articles = article_service.get_articles(
        db=db,
        status=status,
        author_id=author_id,
        category_id=category_id,
        skip=skip,
        limit=limit,
    )
    
    # Get total count
    total = article_service.count_articles(
        db=db,
        status=status,
        author_id=author_id,
        category_id=category_id,
    )
    
    return {
        "items": articles,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{article_id}", response_model=KnowledgeArticleResponse)
def get_article(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get article by ID."""
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Requesters can only view published articles
    if current_user.role == "requester" and article.status != "PUBLISHED":
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count for published articles
    if article.status == "PUBLISHED":
        article = article_service.increment_view_count(db, article)
    
    return article


@router.patch("/{article_id}", response_model=KnowledgeArticleResponse)
def update_article(
    article_id: str,
    article_data: KnowledgeArticleUpdate,
    current_user: User = Depends(get_current_operator),
    db: Session = Depends(get_db),
):
    """Update article (operator/admin only)."""
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Prepare update data
    updates = article_data.model_dump(exclude_unset=True)
    
    # Handle tags separately
    if "tags" in updates:
        tag_names = updates.pop("tags")
        article.tags.clear()
        if tag_names:
            from app.models.tag import Tag
            import uuid
            from datetime import datetime
            for tag_name in tag_names:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(id=str(uuid.uuid4()), name=tag_name, created_at=datetime.utcnow())
                    db.add(tag)
                article.tags.append(tag)
    
    return article_service.update_article(db, article, current_user.id, **updates)


@router.post("/{article_id}/publish", response_model=KnowledgeArticleResponse)
def publish_article(
    article_id: str,
    current_user: User = Depends(get_current_operator),
    db: Session = Depends(get_db),
):
    """Publish an article (operator/admin only)."""
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if article.status == "PUBLISHED":
        raise HTTPException(status_code=400, detail="Article is already published")
    
    return article_service.publish_article(db, article, current_user.id)


@router.post("/{article_id}/unpublish", response_model=KnowledgeArticleResponse)
def unpublish_article(
    article_id: str,
    current_user: User = Depends(get_current_operator),
    db: Session = Depends(get_db),
):
    """Unpublish an article (operator/admin only)."""
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if article.status != "PUBLISHED":
        raise HTTPException(status_code=400, detail="Article is not published")
    
    return article_service.unpublish_article(db, article, current_user.id)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: str,
    current_user: User = Depends(get_current_operator),
    db: Session = Depends(get_db),
):
    """Archive an article (soft delete, operator/admin only)."""
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article.status = "ARCHIVED"
    article.updated_at = __import__("datetime").datetime.utcnow()
    db.commit()
    
    # Create audit log
    from app.services.article_service import _create_audit_log
    _create_audit_log(
        db,
        user_id=current_user.id,
        action="ARTICLE_ARCHIVED",
        entity_type="ARTICLE",
        entity_id=article.id,
        metadata={"title": article.title},
    )
    
    return None
