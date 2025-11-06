import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models.knowledge_article import KnowledgeArticle
from app.models.tag import Tag
from app.models.audit_log import AuditLog


def create_article(
    db: Session,
    title: str,
    content: str,
    author_id: str,
    category_id: Optional[str] = None,
    tag_names: Optional[List[str]] = None,
) -> KnowledgeArticle:
    """Create a new knowledge article (draft)."""
    article = KnowledgeArticle(
        id=str(uuid.uuid4()),
        title=title,
        content=content,
        status="DRAFT",
        author_id=author_id,
        category_id=category_id,
        view_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    # Add tags if provided
    if tag_names:
        for tag_name in tag_names:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(id=str(uuid.uuid4()), name=tag_name, created_at=datetime.utcnow())
                db.add(tag)
            article.tags.append(tag)
    
    db.add(article)
    db.commit()
    db.refresh(article)
    
    # Reload article with relationships
    article = get_article(db, article.id)
    
    # Create audit log
    _create_audit_log(
        db,
        user_id=author_id,
        action="ARTICLE_CREATED",
        entity_type="ARTICLE",
        entity_id=article.id,
        metadata={"title": title, "status": "DRAFT"},
    )
    
    return article


def get_article(db: Session, article_id: str) -> Optional[KnowledgeArticle]:
    """Get article by ID."""
    return (
        db.query(KnowledgeArticle)
        .options(
            joinedload(KnowledgeArticle.category),
            joinedload(KnowledgeArticle.author),
            joinedload(KnowledgeArticle.tags),
        )
        .filter(KnowledgeArticle.id == article_id)
        .first()
    )


def get_articles(
    db: Session,
    status: Optional[str] = None,
    author_id: Optional[str] = None,
    category_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 25,
) -> List[KnowledgeArticle]:
    """Get articles with filters."""
    query = db.query(KnowledgeArticle).options(
        joinedload(KnowledgeArticle.category),
        joinedload(KnowledgeArticle.author),
        joinedload(KnowledgeArticle.tags),
    )
    
    if status:
        query = query.filter(KnowledgeArticle.status == status)
    if author_id:
        query = query.filter(KnowledgeArticle.author_id == author_id)
    if category_id:
        query = query.filter(KnowledgeArticle.category_id == category_id)
    
    return query.order_by(KnowledgeArticle.created_at.desc()).offset(skip).limit(limit).all()


def count_articles(
    db: Session,
    status: Optional[str] = None,
    author_id: Optional[str] = None,
    category_id: Optional[str] = None,
) -> int:
    """Count articles with filters."""
    query = db.query(KnowledgeArticle)
    
    if status:
        query = query.filter(KnowledgeArticle.status == status)
    if author_id:
        query = query.filter(KnowledgeArticle.author_id == author_id)
    if category_id:
        query = query.filter(KnowledgeArticle.category_id == category_id)
    
    return query.count()


def update_article(
    db: Session,
    article: KnowledgeArticle,
    user_id: str,
    **updates,
) -> KnowledgeArticle:
    """Update article fields."""
    old_values = {}
    
    for key, value in updates.items():
        if value is not None and hasattr(article, key):
            old_values[key] = getattr(article, key)
            setattr(article, key, value)
    
    article.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(article)
    
    # Create audit log
    if old_values:
        _create_audit_log(
            db,
            user_id=user_id,
            action="ARTICLE_UPDATED",
            entity_type="ARTICLE",
            entity_id=article.id,
            metadata={"old": old_values, "new": updates},
        )
    
    return article


def publish_article(
    db: Session,
    article: KnowledgeArticle,
    user_id: str,
) -> KnowledgeArticle:
    """Publish an article."""
    article.status = "PUBLISHED"
    article.published_at = datetime.utcnow()
    article.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(article)
    
    # Create audit log
    _create_audit_log(
        db,
        user_id=user_id,
        action="ARTICLE_PUBLISHED",
        entity_type="ARTICLE",
        entity_id=article.id,
        metadata={"title": article.title},
    )
    
    return article


def unpublish_article(
    db: Session,
    article: KnowledgeArticle,
    user_id: str,
) -> KnowledgeArticle:
    """Unpublish an article (back to draft)."""
    article.status = "DRAFT"
    article.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(article)
    
    # Create audit log
    _create_audit_log(
        db,
        user_id=user_id,
        action="ARTICLE_UNPUBLISHED",
        entity_type="ARTICLE",
        entity_id=article.id,
        metadata={"title": article.title},
    )
    
    return article


def increment_view_count(
    db: Session,
    article: KnowledgeArticle,
) -> KnowledgeArticle:
    """Increment article view count."""
    article.view_count += 1
    db.commit()
    db.refresh(article)
    return article


def _create_audit_log(
    db: Session,
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    metadata: Optional[dict] = None,
) -> AuditLog:
    """Create an audit log entry."""
    log = AuditLog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        meta_data=metadata,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    return log
