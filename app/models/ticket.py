from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True)
    ticket_number = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)  # OPEN, IN_PROGRESS, WAITING_CUSTOMER, RESOLVED, CLOSED, CANCELED
    priority = Column(String, nullable=False)  # LOW, MEDIUM, HIGH, URGENT
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    requester_id = Column(String, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    assigned_team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    
    # SLA tracking
    first_response_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    waiting_customer_started_at = Column(DateTime, nullable=True)
    total_waiting_customer_duration = Column(Integer, default=0, nullable=False)  # seconds
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("Category", foreign_keys=[category_id])
    requester = relationship("User", foreign_keys=[requester_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    assigned_team = relationship("Team", foreign_keys=[assigned_team_id])
    tags = relationship("Tag", secondary="ticket_tags", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket")
