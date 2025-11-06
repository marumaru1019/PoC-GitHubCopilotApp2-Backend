from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # DRAFT, PUBLISHED, ARCHIVED
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    category = relationship("Category", foreign_keys=[category_id])
    author = relationship("User", foreign_keys=[author_id])
    tags = relationship("Tag", secondary="article_tags", back_populates="articles")
