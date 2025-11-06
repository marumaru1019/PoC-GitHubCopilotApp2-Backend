from datetime import datetime
from sqlalchemy import Column, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

# Association tables
ticket_tags = Table(
    "ticket_tags",
    Base.metadata,
    Column("ticket_id", String, ForeignKey("tickets.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id"), primary_key=True),
)

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", String, ForeignKey("knowledge_articles.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tickets = relationship("Ticket", secondary="ticket_tags", back_populates="tags")
    articles = relationship("KnowledgeArticle", secondary="article_tags", back_populates="tags")
